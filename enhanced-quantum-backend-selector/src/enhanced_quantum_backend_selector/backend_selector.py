"""
Main backend selector for intelligent quantum backend selection.

This module provides the primary public API for selecting optimal backends
based on circuit requirements and multi-criteria scoring.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.backend_analyzer import BackendAnalyzer
from enhanced_quantum_backend_selector.models import BackendRecommendation, CircuitScore


class BackendSelector:
    """
    Intelligent quantum backend selector with multi-criteria scoring.

    Analyzes and ranks backends based on circuit requirements considering:
    - Hardware quality (gate fidelity, coherence times)
    - Circuit compatibility (qubit count, gate set, connectivity)
    - Availability (queue depth, operational status)

    Attributes:
        backends: List of available backends to select from.

    Examples:
        >>> from qiskit_aer import AerSimulator
        >>> from qiskit import QuantumCircuit
        >>>
        >>> # Initialize with available backends
        >>> backends = [AerSimulator(), ...]
        >>> selector = BackendSelector(backends)
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
        >>> print(f"Score: {recommendation.score_data.score:.2f}")
        >>>
        >>> # Or rank all backends
        >>> rankings = selector.rank_backends(qc)
        >>> for i, rec in enumerate(rankings[:3], 1):
        ...     print(f"{i}. {rec.backend.name}: {rec.score_data.score:.2f}")
    """

    def __init__(
        self,
        backends: list[BackendV2],
        transpilation_runs: int = 3,
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

        Raises:
            ValueError: If backends list is empty or transpilation_runs < 1.
        """
        if not backends:
            raise ValueError("backends list cannot be empty")

        if transpilation_runs < 1:
            raise ValueError("transpilation_runs must be at least 1")

        self.backends = backends
        self.transpilation_runs = transpilation_runs
        self._analyzer_cache: dict[str, BackendAnalyzer] = {}

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
            require_compatible: Only consider compatible backends (sufficient
                qubits, supported gates). If True and no compatible backends
                exist, raises an exception.
            min_score: Minimum acceptable score. Backends below this
                threshold are excluded. Note: scores are negative (error sums),
                so -0.01 is better than -0.05.

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
        if circuit.num_qubits == 0:
            raise ValueError("Circuit must have at least one qubit")

        if len(circuit.data) == 0:
            raise ValueError("Circuit has no operations")

        # Rank all backends
        ranked = self.rank_backends(circuit)

        # Filter by compatibility if required
        if require_compatible:
            ranked = [r for r in ranked if r.score_data.compatible]
            if not ranked:
                gates = {instr.operation.name for instr in circuit.data}
                raise RuntimeError(
                    "No compatible backends found. "
                    f"Circuit requires {circuit.num_qubits} qubits and "
                    f"uses gates: {gates}"
                )

        # Filter by minimum score if specified
        if min_score is not None:
            ranked = [r for r in ranked if r.score_data.score >= min_score]
            if not ranked:
                raise RuntimeError(
                    f"No backends meet minimum score threshold of {min_score}. "
                    "Try lowering the threshold or using different scoring weights."
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

        Args:
            circuit: The quantum circuit to analyze and match against backends.
            top_n: Return only the top N results. If None, returns all.

        Returns:
            List of BackendRecommendation objects sorted by score (highest first).
            Each recommendation includes backend reference, scores, metrics, and rank.
            Scores are negative error sums where higher (less negative) is better.

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

        # Sort by score (descending)
        recommendations.sort(key=lambda r: r.score_data.score, reverse=True)

        # Assign ranks
        for rank, rec in enumerate(recommendations, start=1):
            rec.rank = rank

        # Return top N if specified
        if top_n is not None:
            return recommendations[:top_n]

        return recommendations

    def clear_cache(self) -> None:
        """
        Clear the analyzer cache to force fresh backend analysis.

        Useful when backend calibrations have been updated or when you want
        to ensure the latest backend information is used.

        Examples:
            >>> selector.clear_cache()  # Force refresh on next ranking
            >>> fresh_rankings = selector.rank_backends(circuit)
        """
        self._analyzer_cache.clear()

    def _score_backends_parallel(
        self,
        circuit: QuantumCircuit,
    ) -> list[BackendRecommendation]:
        """
        Score backends in parallel using ThreadPoolExecutor.

        Each backend is automatically evaluated with both standard and fractional
        gate configurations, keeping the best result.

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
                try:
                    recommendation = future.result()
                    recommendations.append(recommendation)
                except Exception as e:
                    backend = future_to_backend[future]
                    # Log error but continue with other backends
                    print(f"Warning: Failed to score backend {backend.name}: {e}")

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
        # Get or create analyzer
        analyzer = self._get_analyzer(backend)

        # Transpile and score multiple times, then average
        scores = []
        all_reasons = []

        for run_num in range(self.transpilation_runs):
            # Transpile the circuit to this backend
            # Each run may produce different results due to stochastic nature
            transpiled = transpile(circuit, backend=backend, optimization_level=2)

            # Score the transpiled circuit
            score_data = analyzer.score_for_circuit(transpiled)
            scores.append(score_data.score)

            # Collect reasons from first run only to avoid duplication
            if run_num == 0:
                all_reasons = score_data.reasons.copy()

        # Calculate average score
        avg_score = sum(scores) / len(scores)

        # Detect if this backend uses fractional gates
        # Expected backend API: backends supporting fractional gates should have
        # a boolean attribute `use_fractional_gates` set to True
        # (set via service.backend(name, use_fractional_gates=True))
        has_fractional = getattr(backend, "use_fractional_gates", False)

        # Create averaged score data
        gate_note = "Using fractional gates" if has_fractional else "Using standard gates"
        averaged_score_data = CircuitScore(
            backend=backend.name,
            compatible=True,  # If transpilation succeeded, it's compatible
            reasons=all_reasons
            + [
                f"Average score over {self.transpilation_runs} transpilation runs: {avg_score:.6f}",
                gate_note,
            ],
            score=avg_score,
        )

        return BackendRecommendation(
            backend=backend,
            score_data=averaged_score_data,
            rank=0,  # Will be assigned during ranking
        )

    def _get_analyzer(self, backend: BackendV2) -> BackendAnalyzer:
        """
        Get or create BackendAnalyzer for a backend.

        Args:
            backend: The backend to analyze.

        Returns:
            BackendAnalyzer instance.
        """
        if backend.name not in self._analyzer_cache:
            self._analyzer_cache[backend.name] = BackendAnalyzer(backend)

        return self._analyzer_cache[backend.name]
