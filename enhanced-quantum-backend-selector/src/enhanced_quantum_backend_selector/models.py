"""
Data models for backend analysis and circuit scoring.

This module contains dataclasses used throughout the enhanced quantum backend selector.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qiskit.providers import BackendV2

# Operations to skip when calculating gate errors (non-gate operations)
SKIP_OPERATIONS = frozenset(["measure", "delay", "reset"])


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
