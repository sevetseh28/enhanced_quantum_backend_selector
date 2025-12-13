"""
Main backend selector for intelligent quantum backend selection.

This module provides the primary public API for selecting optimal backends
based on circuit requirements and multi-criteria scoring.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.exploration.backend_analyzer import BackendAnalyzer
from enhanced_quantum_backend_selector.models import BackendMetrics, BackendRecommendation, CircuitScore
from enhanced_quantum_backend_selector.scoring_weights import ScoringWeights


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

    # Cache TTL: 1 hour (backend calibrations change slowly)
    CACHE_TTL_SECONDS: float = 3600.0

    def __init__(self, backends: List[BackendV2]) -> None:
        """
        Initialize the backend selector.

        Args:
            backends: List of BackendV2 instances to select from.

        Raises:
            ValueError: If backends list is empty.
        """
        if not backends:
            raise ValueError("backends list cannot be empty")

        self.backends = backends
        self._metrics_cache: Dict[str, Tuple[BackendMetrics, float]] = {}
        self._analyzer_cache: Dict[str, BackendAnalyzer] = {}

    def select_backend(
        self,
        circuit: QuantumCircuit,
        weights: Optional[ScoringWeights] = None,
        require_compatible: bool = True,
        min_score: Optional[float] = None,
    ) -> BackendRecommendation:
        """
        Select the best backend for a quantum circuit.

        Ranks all backends and returns the top recommendation based on
        multi-criteria scoring.

        Args:
            circuit: The quantum circuit to execute.
            weights: Custom scoring weights. If None, uses defaults.
            require_compatible: Only consider compatible backends (sufficient
                qubits, supported gates). If True and no compatible backends
                exist, raises an exception.
            min_score: Minimum acceptable score (0-100). Backends below this
                threshold are excluded.

        Returns:
            BackendRecommendation with the highest-scored backend and details.

        Raises:
            ValueError: If circuit is empty or has no operations.
            RuntimeError: If no backend meets the compatibility or score requirements.

        Examples:
            >>> # Simple selection
            >>> best = selector.select_backend(circuit)
            >>>
            >>> # With custom weights (prioritize fast execution)
            >>> fast_weights = ScoringWeights(queue_weight=2.0)
            >>> best = selector.select_backend(circuit, weights=fast_weights)
            >>>
            >>> # With minimum quality threshold
            >>> best = selector.select_backend(circuit, min_score=75.0)
        """
        if circuit.num_qubits == 0:
            raise ValueError("Circuit must have at least one qubit")

        if len(circuit.data) == 0:
            raise ValueError("Circuit has no operations")

        # Rank all backends
        ranked = self.rank_backends(circuit, weights=weights)

        # Filter by compatibility if required
        if require_compatible:
            ranked = [r for r in ranked if r.score_data.compatible]
            if not ranked:
                raise RuntimeError(
                    "No compatible backends found. "
                    f"Circuit requires {circuit.num_qubits} qubits and "
                    f"uses gates: {set(instr.operation.name for instr in circuit.data)}"
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
        weights: Optional[ScoringWeights] = None,
        top_n: Optional[int] = None,
    ) -> List[BackendRecommendation]:
        """
        Rank all backends for a quantum circuit.

        Analyzes each backend against circuit requirements using multi-criteria
        scoring. Backends are sorted by total score in descending order.

        Args:
            circuit: The quantum circuit to analyze and match against backends.
            weights: Custom scoring weights for criteria. If None, uses defaults
                (fidelity=1.5, connectivity=1.0, coherence=0.8, queue=0.4).
            top_n: Return only the top N results. If None, returns all.

        Returns:
            List of BackendRecommendation objects sorted by score (highest first).
            Each recommendation includes backend reference, scores, metrics, and rank.

        Raises:
            ValueError: If circuit is empty or has no operations.

        Examples:
            >>> # Rank all backends
            >>> ranked = selector.rank_backends(circuit)
            >>> for rec in ranked[:5]:
            ...     print(f"{rec.rank}. {rec.backend.name}: {rec.score_data.score:.2f}")
            >>>
            >>> # Get top 3 with custom weights
            >>> weights = ScoringWeights(gate_fidelity_weight=3.0)
            >>> top3 = selector.rank_backends(circuit, weights=weights, top_n=3)
        """
        if circuit.num_qubits == 0:
            raise ValueError("Circuit must have at least one qubit")

        if len(circuit.data) == 0:
            raise ValueError("Circuit has no operations")

        if weights is None:
            weights = ScoringWeights()

        # Score backends in parallel for performance
        recommendations = self._score_backends_parallel(circuit, weights)

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
        Clear the metrics cache to force fresh backend queries.

        Useful when backend calibrations have been updated or when you want
        to ensure the latest backend information is used.

        Examples:
            >>> selector.clear_cache()  # Force refresh on next ranking
            >>> fresh_rankings = selector.rank_backends(circuit)
        """
        self._metrics_cache.clear()

    def _score_backends_parallel(
        self,
        circuit: QuantumCircuit,
        weights: ScoringWeights,
    ) -> List[BackendRecommendation]:
        """
        Score backends in parallel using ThreadPoolExecutor.

        Note: If you want to compare backends with/without fractional gates,
        you should retrieve both versions from IBM Quantum service and include
        them in the backends list passed to BackendSelector.

        Args:
            circuit: The quantum circuit to score against.
            weights: Scoring weights to apply.

        Returns:
            List of BackendRecommendation objects (unranked).
        """
        recommendations: List[BackendRecommendation] = []

        # Use ThreadPoolExecutor for parallel scoring (max 10 workers)
        max_workers = min(10, len(self.backends))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scoring tasks
            future_to_backend = {
                executor.submit(self._score_single_backend, backend, circuit, weights): backend
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
        weights: ScoringWeights,
    ) -> BackendRecommendation:
        """
        Score a single backend for the circuit.

        Transpiles the circuit 3 times (since transpilation is stochastic)
        and averages the scores to get a more accurate assessment.

        Args:
            backend: The backend to score.
            circuit: The circuit to score against.
            weights: Scoring weights to apply.

        Returns:
            BackendRecommendation for this backend.
        """
        # Get or create analyzer
        analyzer = self._get_analyzer(backend)

        # Get cached or fresh metrics
        metrics = self._get_metrics(analyzer)

        # Transpile and score 3 times, then average
        scores = []
        all_reasons = []
        
        for run_num in range(3):
            # Transpile the circuit to this backend
            # Each run may produce different results due to stochastic nature
            transpiled = transpile(
                circuit, 
                backend=backend, 
                optimization_level=2
            )
            
            # Score the transpiled circuit
            score_data = analyzer.score_for_circuit(transpiled)
            scores.append(score_data.score)
            
            # Collect reasons from first run only to avoid duplication
            if run_num == 0:
                all_reasons = score_data.reasons.copy()
        
        # Calculate average score
        avg_score = sum(scores) / len(scores)
        
        # Create averaged score data
        from enhanced_quantum_backend_selector.models import CircuitScore
        averaged_score_data = CircuitScore(
            backend=backend.name,
            compatible=True,  # If transpilation succeeded, it's compatible
            reasons=all_reasons + [
                f"Average score over 3 transpilation runs: {avg_score:.6f}"
            ],
            score=avg_score,
        )

        return BackendRecommendation(
            backend=backend,
            score_data=averaged_score_data,
            metrics=metrics,
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

    def _get_metrics(self, analyzer: BackendAnalyzer) -> BackendMetrics:
        """
        Get cached or extract fresh metrics for a backend.

        Implements 1-hour TTL caching to minimize backend queries.

        Args:
            analyzer: The BackendAnalyzer instance.

        Returns:
            BackendMetrics for the backend.
        """
        backend_name = analyzer.backend.name
        current_time = time.time()

        # Check cache
        if backend_name in self._metrics_cache:
            cached_metrics, timestamp = self._metrics_cache[backend_name]
            age = current_time - timestamp

            # Return cached if still valid (within TTL)
            if age < self.CACHE_TTL_SECONDS:
                return cached_metrics

        # Extract fresh metrics
        metrics = analyzer.extract_metrics()

        # Update cache
        self._metrics_cache[backend_name] = (metrics, current_time)

        return metrics
