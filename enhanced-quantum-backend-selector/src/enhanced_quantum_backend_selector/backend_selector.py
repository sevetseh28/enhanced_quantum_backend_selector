"""
Main backend selector for intelligent quantum backend selection.

This module provides the primary public API for selecting optimal backends
based on transpilation-based error analysis.
"""

from __future__ import annotations

import logging
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.circuit_scorer import CircuitScorer
from enhanced_quantum_backend_selector.models import BackendRecommendation, CircuitScore

logger = logging.getLogger(__name__)


class BackendSelector:
    """
    Intelligent quantum backend selector based on transpiled circuit error.

    For each backend, the circuit is transpiled to the device and scored by its
    expected error: the gate errors on the physical qubits the transpiler chose,
    plus their readout errors. Backends are considered incompatible when:
    - the circuit needs more qubits than the backend has,
    - the backend reports that it is not operational, or
    - transpilation to the backend fails.

    Attributes:
        backends: List of available backends to select from.
        transpilation_runs: Number of transpilations averaged per backend.
        seed: Base seed for the transpiler, or None for non-deterministic runs.

    Examples:
        >>> from qiskit.providers.fake_provider import GenericBackendV2
        >>> from qiskit import QuantumCircuit
        >>>
        >>> # Initialize with available backends
        >>> backends = [GenericBackendV2(5, seed=1), GenericBackendV2(7, seed=2)]
        >>> selector = BackendSelector(backends, seed=42)
        >>>
        >>> # Create a circuit
        >>> qc = QuantumCircuit(3)
        >>> qc.h(0)
        >>> qc.cx(0, 1)
        >>> qc.cx(1, 2)
        >>>
        >>> # Get best backend
        >>> recommendation = selector.select_backend(qc)
        >>> print(f"Best: {recommendation.backend.name}")
        >>> print(f"Score: {recommendation.score_data.score:.4f}")
        >>>
        >>> # Or rank all backends
        >>> rankings = selector.rank_backends(qc)
        >>> for i, rec in enumerate(rankings[:3], 1):
        ...     print(f"{i}. {rec.backend.name}: {rec.score_data.score:.4f}")
    """

    def __init__(
        self,
        backends: list[BackendV2],
        transpilation_runs: int = 3,
        seed: int | None = None,
    ) -> None:
        """
        Initialize the backend selector.

        For chemistry circuits, you can include both standard and fractional gate
        versions of the same backend to let the selector choose the best one:

        ```python
        backends = [
            service.backend('ibm_torino'),  # Standard gates
            service.backend('ibm_torino', use_fractional_gates=True),  # Fractional gates
            # ... other backends
        ]
        selector = BackendSelector(backends)
        ```

        Args:
            backends: List of BackendV2 instances to select from. Can include
                multiple versions of the same backend with different configurations.
            transpilation_runs: Number of times to transpile each circuit for
                averaging (default: 3). Higher values improve accuracy but increase
                computation time. Must be at least 1.
            seed: Seed for the transpiler. With a seed, the same inputs always produce
                the same ranking. Run ``i`` uses ``seed + i``. If None (default),
                each call may produce slightly different scores.

        Raises:
            ValueError: If backends list is empty or transpilation_runs < 1.
        """
        if not backends:
            raise ValueError("backends list cannot be empty")

        if transpilation_runs < 1:
            raise ValueError("transpilation_runs must be at least 1")

        self.backends = backends
        self.transpilation_runs = transpilation_runs
        self.seed = seed

    def select_backend(
        self,
        circuit: QuantumCircuit,
        require_compatible: bool = True,
        min_score: float | None = None,
    ) -> BackendRecommendation:
        """
        Select the best backend for a quantum circuit.

        Ranks all backends and returns the top recommendation based on
        transpilation-based error analysis.

        Args:
            circuit: The quantum circuit to execute.
            require_compatible: Only consider compatible backends (enough qubits,
                operational, and the circuit transpiles). If True and no compatible
                backends exist, raises an exception.
            min_score: Minimum acceptable score. Backends below this
                threshold are excluded. Scores are negative expected errors,
                so -0.01 (1% error) is better than -0.05 (5% error).

        Returns:
            BackendRecommendation with the highest-scored backend and details.

        Raises:
            ValueError: If circuit is empty or has no operations.
            RuntimeError: If no backend meets the compatibility or score requirements.

        Examples:
            >>> # Simple selection
            >>> best = selector.select_backend(circuit)
            >>>
            >>> # With minimum quality threshold (< 5% expected error)
            >>> best = selector.select_backend(circuit, min_score=-0.05)
        """
        ranked = self.rank_backends(circuit)

        # Filter by compatibility if required
        if require_compatible:
            ranked = [r for r in ranked if r.score_data.compatible]
            if not ranked:
                gates = sorted({instr.operation.name for instr in circuit.data})
                raise RuntimeError(
                    "No compatible backends found. "
                    f"Circuit requires {circuit.num_qubits} qubits and "
                    f"uses gates: {gates}. See each backend's score_data.reasons "
                    "from rank_backends() for details."
                )

        # Filter by minimum score if specified
        if min_score is not None:
            ranked = [r for r in ranked if r.score_data.score >= min_score]
            if not ranked:
                raise RuntimeError(
                    f"No backends meet minimum score threshold of {min_score}. "
                    "Try lowering the threshold or adding more backends."
                )

        return ranked[0]

    def rank_backends(
        self,
        circuit: QuantumCircuit,
        top_n: int | None = None,
    ) -> list[BackendRecommendation]:
        """
        Rank all backends for a quantum circuit.

        Analyzes each backend against circuit requirements using transpilation-based
        error analysis. Backends are sorted by score (highest/least negative first).
        Incompatible backends are included with ``compatible=False`` and a score of
        ``-inf``, so they always rank last.

        Args:
            circuit: The quantum circuit to analyze and match against backends.
            top_n: Return only the top N results. If None, returns all.

        Returns:
            List of BackendRecommendation objects sorted by score (highest first).
            Each recommendation includes backend reference, scores, reasons, and rank.

        Raises:
            ValueError: If circuit is empty or has no operations.

        Examples:
            >>> # Rank all backends
            >>> ranked = selector.rank_backends(circuit)
            >>> for rec in ranked[:5]:
            ...     error_pct = -rec.score_data.score * 100
            ...     print(f"#{rec.rank}. {rec.backend.name}: {error_pct:.2f}% error")
            >>>
            >>> # Get top 3 only
            >>> top3 = selector.rank_backends(circuit, top_n=3)
        """
        if circuit.num_qubits == 0:
            raise ValueError("Circuit must have at least one qubit")

        if len(circuit.data) == 0:
            raise ValueError("Circuit has no operations")

        # Score backends in parallel for performance
        recommendations = self._score_backends_parallel(circuit)

        # Sort by success probability (descending), using the input order to break ties.
        # The log keeps deep circuits apart where score rounds to -1.0 for every backend.
        order = {id(backend): i for i, backend in enumerate(self.backends)}
        recommendations.sort(
            key=lambda r: (-r.score_data.log_success_probability, order[id(r.backend)])
        )

        # Assign ranks
        for rank, rec in enumerate(recommendations, start=1):
            rec.rank = rank

        # Return top N if specified
        if top_n is not None:
            return recommendations[:top_n]

        return recommendations

    def _score_backends_parallel(
        self,
        circuit: QuantumCircuit,
    ) -> list[BackendRecommendation]:
        """
        Score backends in parallel using ThreadPoolExecutor.

        A backend that fails to score is logged and returned as incompatible,
        so one bad backend never hides the others.

        Args:
            circuit: The quantum circuit to score against.

        Returns:
            List of BackendRecommendation objects (unranked).
        """
        recommendations: list[BackendRecommendation] = []

        # Use ThreadPoolExecutor for parallel scoring (max 10 workers)
        max_workers = min(10, len(self.backends))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scoring tasks
            future_to_backend = {
                executor.submit(self._score_single_backend, backend, circuit): backend
                for backend in self.backends
            }

            # Collect results as they complete
            for future in as_completed(future_to_backend):
                backend = future_to_backend[future]
                try:
                    recommendations.append(future.result())
                except Exception as e:
                    logger.warning("Failed to score backend %s: %s", backend.name, e)
                    recommendations.append(
                        _incompatible(backend, f"Failed to transpile or score: {e}")
                    )

        return recommendations

    def _score_single_backend(
        self,
        backend: BackendV2,
        circuit: QuantumCircuit,
    ) -> BackendRecommendation:
        """
        Score a single backend for the circuit.

        Transpiles the circuit multiple times (since transpilation is stochastic)
        and averages the scores to get a more accurate assessment.

        Args:
            backend: The backend to score.
            circuit: The circuit to score against.

        Returns:
            BackendRecommendation for this backend.
        """
        if circuit.num_qubits > backend.num_qubits:
            return _incompatible(
                backend,
                f"Circuit needs {circuit.num_qubits} qubits, " f"backend has {backend.num_qubits}",
            )

        not_operational = _not_operational_reason(backend)
        if not_operational:
            return _incompatible(backend, not_operational)

        # Create scorer for this backend
        scorer = CircuitScorer(backend)

        # Transpile and score multiple times, then average
        log_successes = []
        all_reasons: list[str] = []

        for run_num in range(self.transpilation_runs):
            seed = None if self.seed is None else self.seed + run_num
            transpiled = transpile(
                circuit, backend=backend, optimization_level=2, seed_transpiler=seed
            )

            # Score the transpiled circuit
            score_data = scorer.score_circuit(transpiled)
            log_successes.append(score_data.log_success_probability)

            # Collect reasons from first run only to avoid duplication
            if run_num == 0:
                all_reasons = score_data.reasons.copy()

        # Average the success probabilities, computed in log space so deep circuits
        # don't underflow, and derive the score from it so score and ranking always
        # agree. expm1(x) == -(1 - e^x).
        avg_log_success = _log_mean_exp(log_successes)
        avg_score = math.expm1(avg_log_success)

        # Note whether this backend instance was created with fractional gates
        # (service.backend(name, use_fractional_gates=True)). The selector does not
        # try both variants itself: pass both instances to compare them.
        has_fractional = getattr(backend, "use_fractional_gates", False)

        # Create averaged score data
        gate_note = "Using fractional gates" if has_fractional else "Using standard gates"
        success_text = _format_probability(avg_log_success)
        averaged_score_data = CircuitScore(
            backend=backend.name,
            compatible=True,
            reasons=all_reasons
            + [
                f"Average over {self.transpilation_runs} transpilation runs: "
                f"score {avg_score:.6f}, success probability {success_text}",
                gate_note,
            ],
            score=avg_score,
            log_success_probability=avg_log_success,
        )

        return BackendRecommendation(
            backend=backend,
            score_data=averaged_score_data,
            rank=0,  # Will be assigned during ranking
        )


def _log_mean_exp(values: list[float]) -> float:
    """Log of the mean of ``exp(values)``, without underflow for very negative values."""
    peak = max(values)
    if peak == float("-inf"):
        return peak
    return peak + math.log(sum(math.exp(v - peak) for v in values) / len(values))


def _format_probability(log_probability: float) -> str:
    """Format a probability given as a log, falling back to e^x when it underflows."""
    probability = math.exp(log_probability)
    return f"{probability:.3g}" if probability > 0 else f"e^{log_probability:.1f}"


def _incompatible(backend: BackendV2, reason: str) -> BackendRecommendation:
    """Build a recommendation for a backend that cannot run the circuit."""
    return BackendRecommendation(
        backend=backend,
        score_data=CircuitScore(
            backend=backend.name,
            compatible=False,
            reasons=[reason],
            score=float("-inf"),
            log_success_probability=float("-inf"),
        ),
        rank=0,
    )


def _not_operational_reason(backend: BackendV2) -> str | None:
    """
    Return why the backend is not operational, or None if it is (or can't tell).

    ``BackendV2`` has no standard status API, so this relies on the ``status()``
    method that providers such as qiskit-ibm-runtime expose.
    """
    status_method = getattr(backend, "status", None)
    if not callable(status_method):
        return None
    try:
        status = status_method()
    except Exception as e:
        logger.debug("Could not get status of backend %s: %s", backend.name, e)
        return None
    if getattr(status, "operational", True) is False:
        message = getattr(status, "status_msg", "") or "no status message"
        return f"Backend is not operational ({message})"
    return None
