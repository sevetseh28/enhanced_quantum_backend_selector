"""
Main backend selector for intelligent quantum backend selection.

This module provides the primary public API for selecting optimal backends
based on circuit requirements and multi-criteria scoring.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2
from qiskit.transpiler.exceptions import TranspilerError

from enhanced_quantum_backend_selector.exploration.backend_analyzer import BackendAnalyzer
from enhanced_quantum_backend_selector.models import (
    AggregatedScore,
    BackendMetrics,
    BackendRecommendation,
    CircuitScore,
    ScoringConfiguration,
    TranspilationRun,
)
from enhanced_quantum_backend_selector.scoring_weights import ScoringWeights

logger = logging.getLogger(__name__)


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

    def __init__(self, backends: list[BackendV2]) -> None:
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
        self._metrics_cache: dict[str, tuple[BackendMetrics, float]] = {}
        self._analyzer_cache: dict[str, BackendAnalyzer] = {}
        self._calibration_cache: dict[str, tuple[object, float]] = {}

    def select_backend(
        self,
        circuit: QuantumCircuit,
        weights: ScoringWeights | None = None,
        require_compatible: bool = True,
        min_score: float | None = None,
        config: ScoringConfiguration | None = None,
    ) -> BackendRecommendation:
        """
        Select the best backend for a quantum circuit.

        Ranks all backends and returns the top recommendation based on
        multi-criteria scoring with transpiled circuit error analysis.

        Args:
            circuit: The quantum circuit to execute.
            weights: Custom scoring weights. If None, uses defaults.
            require_compatible: Only consider compatible backends (sufficient
                qubits, supported gates). If True and no compatible backends
                exist, raises an exception.
            min_score: Minimum acceptable score (0-100). Backends below this
                threshold are excluded.
            config: Transpilation scoring configuration. If None, uses defaults
                (3 runs, mean aggregation, both fractional gate modes).

        Returns:
            BackendRecommendation with the highest-scored backend and details.

        Raises:
            ValueError: If circuit is empty or has no operations.
            RuntimeError: If no backend meets the compatibility or score requirements.

        Examples:
            >>> # Simple selection
            >>> best = selector.select_backend(circuit)
            >>>
            >>> # With custom configuration
            >>> config = ScoringConfiguration(
            ...     transpilation_runs=5,
            ...     aggregation_method='median'
            ... )
            >>> best = selector.select_backend(circuit, config=config)
            >>>
            >>> # With minimum quality threshold
            >>> best = selector.select_backend(circuit, min_score=75.0)
        """
        if circuit.num_qubits == 0:
            raise ValueError("Circuit must have at least one qubit")

        if len(circuit.data) == 0:
            raise ValueError("Circuit has no operations")

        # Rank all backends
        ranked = self.rank_backends(circuit, weights=weights, config=config)

        # Filter by compatibility if required
        if require_compatible:
            ranked = [r for r in ranked if r.transpilation_details is not None]
            if not ranked:
                raise RuntimeError(
                    "No compatible backends found. "
                    "All backends failed transpilation. "
                    f"Circuit requires {circuit.num_qubits} qubits and "
                    f"uses gates: {
                        {instr.operation.name for instr in circuit.data}
                    }"
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
        weights: ScoringWeights | None = None,
        top_n: int | None = None,
        config: ScoringConfiguration | None = None,
    ) -> list[BackendRecommendation]:
        """
        Rank all backends for a quantum circuit using transpiled error scoring.

        Analyzes each backend against circuit requirements using transpiled
        circuit error sums. Backends are sorted by total score in descending order.

        Args:
            circuit: The quantum circuit to analyze and match against backends.
            weights: Custom scoring weights for criteria. If None, uses defaults.
                (Deprecated: use config.weights instead)
            top_n: Return only the top N results. If None, returns all.
            config: Transpilation scoring configuration. If None, uses defaults
                (3 runs, mean aggregation, both fractional gate modes).

        Returns:
            List of BackendRecommendation objects sorted by score (highest first).
            Each recommendation includes backend reference, scores, metrics, and rank.
            Backends that fail all transpilations are excluded.

        Raises:
            ValueError: If circuit is empty or has no operations.
            ValueError: If all backends fail transpilation.

        Examples:
            >>> # Rank all backends
            >>> ranked = selector.rank_backends(circuit)
            >>> for rec in ranked[:5]:
            ...     print(f"{rec.rank}. {rec.backend.name}: {rec.score_data.score:.2f}")
            >>>
            >>> # Get top 3 with custom config
            >>> config = ScoringConfiguration(aggregation_method='median')
            >>> top3 = selector.rank_backends(circuit, config=config, top_n=3)
        """
        if circuit.num_qubits == 0:
            raise ValueError("Circuit must have at least one qubit")

        if len(circuit.data) == 0:
            raise ValueError("Circuit has no operations")

        # Create config if not provided
        if config is None:
            config = ScoringConfiguration()

        # Handle deprecated weights parameter
        if weights is not None and config.weights is None:
            logger.warning("Passing weights directly is deprecated. Use config.weights instead.")
            config.weights = weights

        if weights is None:
            weights = config.weights or ScoringWeights()

        # Score backends using transpilation
        recommendations = self._score_backends_transpiled(circuit, config)

        # Check if all backends failed
        if not recommendations:
            raise ValueError(
                f"All {len(self.backends)} backends failed transpilation for circuit. "
                f"Check circuit compatibility or reduce circuit depth."
            )

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
        self._calibration_cache.clear()

    def _score_backends_transpiled(
        self,
        circuit: QuantumCircuit,
        config: ScoringConfiguration,
    ) -> list[BackendRecommendation]:
        """
        Score backends using transpiled circuit error analysis.

        Args:
            circuit: The quantum circuit to score against.
            config: Transpilation configuration.

        Returns:
            List of BackendRecommendation objects (excludes failed backends).
        """
        recommendations: list[BackendRecommendation] = []

        # Use ThreadPoolExecutor for parallel scoring (max 10 workers)
        max_workers = min(10, len(self.backends))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scoring tasks
            future_to_backend = {
                executor.submit(
                    self._score_backend_with_transpilation, circuit, backend, config
                ): backend
                for backend in self.backends
            }

            # Collect results as they complete
            for future in as_completed(future_to_backend):
                try:
                    recommendation = future.result()
                    if recommendation is not None:  # Exclude failed backends
                        recommendations.append(recommendation)
                except Exception as e:
                    backend = future_to_backend[future]
                    # Log error but continue with other backends
                    logger.error(f"Failed to score backend {backend.name}: {e}", exc_info=True)

        return recommendations

    def _score_backends_parallel(
        self,
        circuit: QuantumCircuit,
        weights: ScoringWeights,
    ) -> list[BackendRecommendation]:
        """
        Score backends in parallel using ThreadPoolExecutor.

        Args:
            circuit: The quantum circuit to score against.
            weights: Scoring weights to apply.

        Returns:
            List of BackendRecommendation objects (unranked).
        """
        recommendations: list[BackendRecommendation] = []

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

        # Score the circuit
        score_data = analyzer.score_for_circuit(circuit)

        # Apply weights to score (simplified - could be more sophisticated)
        # This is a placeholder - actual implementation would use weights
        # to adjust individual criterion scores before combining

        return BackendRecommendation(
            backend=backend,
            score_data=score_data,
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

    def _get_backend_calibration(self, backend: BackendV2) -> object:
        """
        Get cached or fresh backend calibration data (target).

        Implements 1-hour TTL caching for calibration data.

        Args:
            backend: The backend to get calibration for.

        Returns:
            Backend target with calibration data.
        """
        backend_name = backend.name
        current_time = time.time()

        # Check cache
        if backend_name in self._calibration_cache:
            cached_target, timestamp = self._calibration_cache[backend_name]
            age = current_time - timestamp

            # Return cached if still valid (within TTL)
            if age < self.CACHE_TTL_SECONDS:
                return cached_target

        # Fetch fresh target
        target = backend.target

        # Update cache
        self._calibration_cache[backend_name] = (target, current_time)

        return target

    def _transpile_circuit(
        self,
        circuit: QuantumCircuit,
        backend: BackendV2,
        fractional_gates: bool,
        optimization_level: int,
    ) -> TranspilationRun:
        """
        Transpile circuit for a specific backend configuration.

        Args:
            circuit: Source quantum circuit.
            backend: Target backend.
            fractional_gates: Enable fractional gates (placeholder - API TBD).
            optimization_level: Qiskit optimization level (0-3).

        Returns:
            TranspilationRun with success status and error sum.
        """
        try:
            # Transpile circuit to backend's native gate set
            # Note: fractional_gates parameter handling deferred per research.md
            transpiled = transpile(circuit, backend=backend, optimization_level=optimization_level)

            # Calculate error sum from transpiled circuit
            error_sum, missing_count = self._calculate_error_sum(transpiled, backend)

            # Count instructions
            num_instructions = len(transpiled.data)

            return TranspilationRun(
                circuit=transpiled,
                success=True,
                error_sum=error_sum,
                fractional_gates=fractional_gates,
                num_instructions=num_instructions,
                missing_error_count=missing_count,
            )

        except TranspilerError as e:
            # Transpilation failed - return failure run
            logger.warning(f"Backend {backend.name}: transpilation failed - {str(e)}")
            return TranspilationRun(
                circuit=None,
                success=False,
                error_sum=None,
                failure_reason=f"TranspilerError: {str(e)}",
                fractional_gates=fractional_gates,
            )

        except Exception as e:
            # Unexpected error - return failure run
            logger.warning(f"Backend {backend.name}: unexpected transpilation error - {str(e)}")
            return TranspilationRun(
                circuit=None,
                success=False,
                error_sum=None,
                failure_reason=f"Unexpected error: {str(e)}",
                fractional_gates=fractional_gates,
            )

    def _calculate_error_sum(
        self, transpiled_circuit: QuantumCircuit, backend: BackendV2
    ) -> tuple[float, int]:
        """
        Calculate sum of error rates for all instructions in transpiled circuit.

        Args:
            transpiled_circuit: Circuit with native gates only.
            backend: Backend with calibration data.

        Returns:
            Tuple of (error_sum, missing_count).
        """
        target = self._get_backend_calibration(backend)
        error_sum = 0.0
        missing_count = 0

        # Identity circuit (zero instructions) gets perfect score
        if len(transpiled_circuit.data) == 0:
            return (0.0, 0)

        for instruction in transpiled_circuit.data:
            op_name = instruction.operation.name
            qubits = tuple(transpiled_circuit.find_bit(q).index for q in instruction.qubits)

            try:
                # Extract error rate from target
                if op_name in target:
                    if qubits in target[op_name]:
                        error = target[op_name][qubits].error
                        if error is not None:
                            error_sum += error
                        else:
                            missing_count += 1
                            logger.debug(
                                f"Backend {backend.name}: instruction {op_name} "
                                f"on qubits {qubits} has None error rate"
                            )
                    else:
                        missing_count += 1
                        logger.debug(
                            f"Backend {backend.name}: instruction {op_name} "
                            f"on qubits {qubits} not in target"
                        )
                else:
                    missing_count += 1
                    logger.debug(
                        f"Backend {backend.name}: operation {op_name} " f"not found in target"
                    )

            except (KeyError, AttributeError) as e:
                # Missing error data - skip and count
                missing_count += 1
                logger.debug(
                    f"Backend {backend.name}: error accessing {op_name} "
                    f"on qubits {qubits} - {str(e)}"
                )

        # Warn if significant missing data
        if missing_count > 0:
            logger.warning(
                f"Backend {backend.name}: {missing_count}/{len(transpiled_circuit.data)} "
                f"instructions missing error data"
            )

        return (error_sum, missing_count)

    def _aggregate_scores(
        self, runs: list[TranspilationRun], method: str
    ) -> AggregatedScore | None:
        """
        Aggregate multiple transpilation runs into single score.

        Args:
            runs: List of transpilation attempts.
            method: Aggregation method ('mean', 'median', 'minimum').

        Returns:
            AggregatedScore if any runs succeeded, None if all failed.
        """
        if not runs:
            return None

        try:
            return AggregatedScore.from_runs(runs, method=method)
        except ValueError:
            # No successful runs
            return None

    def _score_backend_with_transpilation(
        self,
        circuit: QuantumCircuit,
        backend: BackendV2,
        config: ScoringConfiguration,
    ) -> BackendRecommendation | None:
        """
        Score a backend using transpiled circuit error-based method.

        Args:
            circuit: Source quantum circuit.
            backend: Backend to score.
            config: Transpilation configuration.

        Returns:
            BackendRecommendation if any transpilations succeeded, None if all failed.
        """
        # Determine which fractional gates configurations to try
        # Note: Fractional gates API research ongoing per research.md
        fractional_configs = []
        if config.fractional_gates_mode == "both":
            fractional_configs = [False, True]
        elif config.fractional_gates_mode == "enabled":
            fractional_configs = [True]
        else:  # disabled
            fractional_configs = [False]

        best_score = None
        best_fractional_config = None

        for fractional_gates in fractional_configs:
            # Run multiple transpilations
            runs: list[TranspilationRun] = []

            # Parallelize transpilations within backend
            max_workers = min(config.transpilation_runs, 4)  # Limit parallelization

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        self._transpile_circuit,
                        circuit,
                        backend,
                        fractional_gates,
                        config.optimization_level,
                    )
                    for _ in range(config.transpilation_runs)
                ]
                runs = [f.result() for f in futures]

            # Aggregate scores
            agg_score = self._aggregate_scores(runs, config.aggregation_method)

            if agg_score is None:
                # All runs failed for this config
                continue

            # Keep best score across fractional gate configs
            if best_score is None or agg_score.final_score < best_score.final_score:
                best_score = agg_score
                best_fractional_config = fractional_gates

        # If all transpilations failed, exclude backend
        if best_score is None:
            last_failure = next(
                (r.failure_reason for r in reversed(runs) if not r.success), "Unknown"
            )
            logger.warning(
                f"Backend {backend.name} excluded: all {len(runs)} "
                f"transpilations failed. Last error: {last_failure}"
            )
            return None

        # Get analyzer and metrics for backward compatibility
        analyzer = self._get_analyzer(backend)
        metrics = self._get_metrics(analyzer)

        # Create circuit score from transpilation error
        # Lower error is better, so invert for score (higher is better)
        # Normalize to 0-100 range
        max_error = 1.0  # Assume max possible error sum is 1.0
        normalized_score = max(0.0, (max_error - best_score.final_score) / max_error * 100)

        score_data = CircuitScore(
            backend=backend.name,
            compatible=True,
            reasons=[
                f"Transpiled successfully with {best_score.successful_runs} runs",
                f"Error sum: {best_score.final_score:.6f}",
                f"Aggregation: {best_score.aggregation_method}",
            ],
            score=normalized_score,
        )

        return BackendRecommendation(
            backend=backend,
            score_data=score_data,
            metrics=metrics,
            rank=0,  # Will be assigned during ranking
            transpilation_details=best_score,
            fractional_gates_used=best_fractional_config if len(fractional_configs) > 1 else None,
        )
