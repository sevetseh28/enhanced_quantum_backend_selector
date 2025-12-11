"""
Data models for backend analysis and circuit scoring.

This module contains dataclasses used throughout the enhanced quantum backend selector.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, median, stdev
from statistics import variance as calc_variance
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qiskit.circuit import QuantumCircuit
    from qiskit.providers import BackendV2

    from enhanced_quantum_backend_selector.scoring_weights import ScoringWeights


@dataclass
class BackendMetrics:
    """Dataclass for backend metrics with comprehensive performance information"""

    # Basic properties
    name: str = ""
    num_qubits: int | None = None
    max_circuits: int | None = None

    # Operations
    num_operations: int = 0
    operations: list[str] = field(default_factory=list)

    # Single-qubit gate errors
    avg_1q_error: float | None = None
    max_1q_error: float | None = None
    min_1q_error: float | None = None

    # Two-qubit gate errors
    avg_2q_error: float | None = None
    max_2q_error: float | None = None
    min_2q_error: float | None = None

    # Readout errors
    avg_readout_error: float | None = None
    max_readout_error: float | None = None

    # Coherence times
    avg_t1: float | None = None
    min_t1: float | None = None
    max_t1: float | None = None
    avg_t2: float | None = None
    min_t2: float | None = None

    # Connectivity
    num_edges: int | None = None
    is_bidirectional: bool | None = None
    connectivity_ratio: float | None = None
    avg_degree: float | None = None

    # Status
    operational: bool | None = None
    pending_jobs: int | None = None


@dataclass
class CircuitScore:
    """
    Circuit scoring results for a specific backend.

    Attributes:
        backend: Name of the backend that was scored.
        compatible: Whether the backend is compatible with the circuit.
        reasons: List of human-readable reasons explaining the score.
        score: Overall score (0-100), higher is better.
    """

    backend: str
    compatible: bool
    reasons: list[str] = field(default_factory=list)
    score: float = 100.0


@dataclass
class BackendRecommendation:
    """
    Complete recommendation for a backend including reference and scoring details.

    This is the primary output type for backend selection, containing everything
    needed to understand why a backend was recommended.

    Attributes:
        backend: The actual BackendV2 instance.
        score_data: Detailed scoring information for the circuit.
        metrics: Extracted metrics from the backend.
        rank: Ranking position (1 = best, 2 = second best, etc.).
        transpilation_details: Aggregated transpilation scores
            (None if not using transpiled scoring).
        fractional_gates_used: Which fractional gates config was used
            (None if both or not applicable).

    Examples:
        >>> recommendations = selector.rank_backends(circuit)
        >>> best = recommendations[0]
        >>> print(f"Recommended: {best.backend.name} (rank {best.rank})")
        >>> print(f"Score: {best.score_data.score:.2f}")
        >>> print(f"Reasons: {', '.join(best.score_data.reasons)}")
    """

    backend: BackendV2
    score_data: CircuitScore
    metrics: BackendMetrics
    rank: int
    transpilation_details: AggregatedScore | None = None
    fractional_gates_used: bool | None = None


@dataclass
class TranspilationRun:
    """Result of a single transpilation attempt.

    Attributes:
        circuit: The transpiled circuit (native gates), None if failed.
        success: Whether transpilation succeeded.
        error_sum: Sum of instruction error rates (None if failed).
        failure_reason: Error message if transpilation failed.
        fractional_gates: Which fractional gates config was used.
        num_instructions: Count of instructions in transpiled circuit.
        missing_error_count: Count of instructions with missing error data.
    """

    circuit: QuantumCircuit | None
    success: bool
    error_sum: float | None
    failure_reason: str | None = None
    fractional_gates: bool = False
    num_instructions: int = 0
    missing_error_count: int = 0

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if self.success and self.error_sum is None:
            raise ValueError("Successful run must have error_sum")
        if not self.success and self.failure_reason is None:
            raise ValueError("Failed run must have failure_reason")


@dataclass
class AggregatedScore:
    """Score aggregated from multiple transpilation runs.

    Attributes:
        final_score: Aggregated error sum (mean/median/minimum).
        individual_scores: Error sums from each successful run.
        aggregation_method: Method used: 'mean', 'median', or 'minimum'.
        successful_runs: Count of successful transpilations.
        failed_runs: Count of failed transpilations.
        variance: Statistical variance of individual scores.
        std_dev: Standard deviation of individual scores.
    """

    final_score: float
    individual_scores: list[float]
    aggregation_method: str
    successful_runs: int
    failed_runs: int
    variance: float | None = None
    std_dev: float | None = None

    def __post_init__(self) -> None:
        """Calculate statistics after initialization."""
        if len(self.individual_scores) != self.successful_runs:
            raise ValueError(
                f"individual_scores length ({len(self.individual_scores)}) "
                f"must match successful_runs ({self.successful_runs})"
            )

        # Calculate variance and std dev if multiple runs
        if self.successful_runs >= 2:
            self.variance = calc_variance(self.individual_scores)
            self.std_dev = stdev(self.individual_scores)

        # Validate aggregation method
        if self.aggregation_method not in ["mean", "median", "minimum"]:
            raise ValueError(f"Invalid aggregation_method: {self.aggregation_method}")

    @classmethod
    def from_runs(cls, runs: list[TranspilationRun], method: str = "mean") -> AggregatedScore:
        """Create AggregatedScore from TranspilationRun list.

        Args:
            runs: List of transpilation attempts.
            method: Aggregation method ('mean', 'median', or 'minimum').

        Returns:
            AggregatedScore with final score and statistics.

        Raises:
            ValueError: If no successful runs or invalid method.
        """
        successful = [r for r in runs if r.success]
        failed = [r for r in runs if not r.success]

        if not successful:
            raise ValueError("No successful transpilation runs to aggregate")

        scores = [r.error_sum for r in successful if r.error_sum is not None]

        if method == "mean":
            final = mean(scores)
        elif method == "median":
            final = median(scores)
        elif method == "minimum":
            final = min(scores)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")

        return cls(
            final_score=final,
            individual_scores=scores,
            aggregation_method=method,
            successful_runs=len(successful),
            failed_runs=len(failed),
        )


@dataclass
class ScoringConfiguration:
    """User-configurable parameters for transpiled circuit scoring.

    Attributes:
        transpilation_runs: Number of transpilation attempts per backend.
        aggregation_method: Statistical measure: 'mean', 'median', or 'minimum'.
        fractional_gates_mode: Evaluation mode: 'both', 'enabled', 'disabled'.
        optimization_level: Qiskit transpiler optimization level (0-3).
        weights: Existing scoring weights (backward compatible).
    """

    transpilation_runs: int = 3
    aggregation_method: str = "mean"
    fractional_gates_mode: str = "both"
    optimization_level: int = 3
    weights: ScoringWeights | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Validate transpilation_runs
        if self.transpilation_runs <= 0:
            raise ValueError(
                f"transpilation_runs must be positive integer, " f"got {self.transpilation_runs}"
            )

        # Validate aggregation_method
        valid_methods = ["mean", "median", "minimum"]
        if self.aggregation_method not in valid_methods:
            raise ValueError(
                f"aggregation_method must be one of {valid_methods}, "
                f"got '{self.aggregation_method}'"
            )

        # Validate fractional_gates_mode
        valid_modes = ["both", "enabled", "disabled"]
        if self.fractional_gates_mode not in valid_modes:
            raise ValueError(
                f"fractional_gates_mode must be one of {valid_modes}, "
                f"got '{self.fractional_gates_mode}'"
            )

        # Validate optimization_level
        if not (0 <= self.optimization_level <= 3):
            raise ValueError(f"optimization_level must be 0-3, got {self.optimization_level}")
