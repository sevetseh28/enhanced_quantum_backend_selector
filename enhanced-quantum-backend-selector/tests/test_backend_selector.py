"""
Unit tests for BackendSelector class.

Tests cover initialization, ranking, selection, caching, and error handling.
"""

import pytest
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from enhanced_quantum_backend_selector import (
    BackendSelector,
    BackendRecommendation,
    ScoringWeights,
)


class TestBackendSelector:
    """Test suite for BackendSelector class."""

    @pytest.fixture
    def backends(self) -> list:
        """Create a list of test backends."""
        # Use AerSimulator as test backends with different qubit counts
        return [
            AerSimulator(),
        ]

    @pytest.fixture
    def simple_circuit(self) -> QuantumCircuit:
        """Create a simple test circuit."""
        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure_all()
        return qc

    def test_init_with_backends(self, backends):
        """Test BackendSelector initialization with valid backends list."""
        selector = BackendSelector(backends)
        assert selector.backends == backends
        assert len(selector._metrics_cache) == 0
        assert len(selector._analyzer_cache) == 0

    def test_init_empty_backends_raises_error(self):
        """Test that initializing with empty backends list raises ValueError."""
        with pytest.raises(ValueError, match="backends list cannot be empty"):
            BackendSelector([])

    def test_rank_backends_returns_list(self, backends, simple_circuit):
        """Test that rank_backends returns a list of recommendations."""
        selector = BackendSelector(backends)
        recommendations = selector.rank_backends(simple_circuit)

        assert isinstance(recommendations, list)
        assert len(recommendations) == len(backends)
        assert all(isinstance(r, BackendRecommendation) for r in recommendations)

    def test_rank_backends_assigns_ranks(self, backends, simple_circuit):
        """Test that rank_backends assigns sequential ranks."""
        selector = BackendSelector(backends)
        recommendations = selector.rank_backends(simple_circuit)

        ranks = [r.rank for r in recommendations]
        assert ranks == list(range(1, len(backends) + 1))

    def test_rank_backends_sorted_by_score(self, backends, simple_circuit):
        """Test that recommendations are sorted by score (descending)."""
        selector = BackendSelector(backends)
        recommendations = selector.rank_backends(simple_circuit)

        scores = [r.score_data.score for r in recommendations]
        assert scores == sorted(scores, reverse=True)

    def test_select_backend_returns_top(self, backends, simple_circuit):
        """Test that select_backend returns the highest-scored backend."""
        selector = BackendSelector(backends)
        best = selector.select_backend(simple_circuit)

        assert isinstance(best, BackendRecommendation)
        assert best.rank == 1

    def test_select_backend_with_custom_weights(self, backends, simple_circuit):
        """Test backend selection with custom scoring weights."""
        selector = BackendSelector(backends)
        custom_weights = ScoringWeights(
            gate_fidelity_weight=2.0,
            connectivity_weight=1.0,
            coherence_weight=0.5,
            queue_weight=0.1,
        )

        best = selector.select_backend(simple_circuit, weights=custom_weights)
        assert isinstance(best, BackendRecommendation)

    def test_rank_backends_with_top_n(self, backends, simple_circuit):
        """Test that top_n parameter limits results."""
        selector = BackendSelector(backends)
        top_1 = selector.rank_backends(simple_circuit, top_n=1)

        assert len(top_1) == 1
        assert top_1[0].rank == 1

    def test_empty_circuit_raises_error(self, backends):
        """Test that empty circuit raises ValueError."""
        selector = BackendSelector(backends)
        empty_circuit = QuantumCircuit(3)  # No operations

        with pytest.raises(ValueError, match="Circuit has no operations"):
            selector.rank_backends(empty_circuit)

    def test_zero_qubit_circuit_raises_error(self, backends):
        """Test that zero-qubit circuit raises ValueError."""
        selector = BackendSelector(backends)
        zero_qubit_circuit = QuantumCircuit(0)

        with pytest.raises(ValueError, match="Circuit must have at least one qubit"):
            selector.rank_backends(zero_qubit_circuit)

    def test_clear_cache(self, backends, simple_circuit):
        """Test that clear_cache empties the metrics cache."""
        selector = BackendSelector(backends)

        # First ranking populates cache
        selector.rank_backends(simple_circuit)
        assert len(selector._metrics_cache) > 0

        # Clear cache
        selector.clear_cache()
        assert len(selector._metrics_cache) == 0

    def test_metrics_caching(self, backends, simple_circuit):
        """Test that metrics are cached between calls."""
        selector = BackendSelector(backends)

        # First call
        selector.rank_backends(simple_circuit)
        cache_size_after_first = len(selector._metrics_cache)

        # Second call should reuse cache
        selector.rank_backends(simple_circuit)
        cache_size_after_second = len(selector._metrics_cache)

        assert cache_size_after_first == cache_size_after_second
        assert cache_size_after_first == len(backends)


class TestScoringWeights:
    """Test suite for ScoringWeights dataclass."""

    def test_default_weights(self):
        """Test default weight values."""
        weights = ScoringWeights()

        assert weights.gate_fidelity_weight == 1.5
        assert weights.connectivity_weight == 1.0
        assert weights.coherence_weight == 0.8
        assert weights.queue_weight == 0.4

    def test_custom_weights(self):
        """Test custom weight values."""
        weights = ScoringWeights(
            gate_fidelity_weight=2.0,
            connectivity_weight=1.5,
            coherence_weight=1.0,
            queue_weight=0.5,
        )

        assert weights.gate_fidelity_weight == 2.0
        assert weights.connectivity_weight == 1.5
        assert weights.coherence_weight == 1.0
        assert weights.queue_weight == 0.5

    def test_negative_weight_raises_error(self):
        """Test that negative weights raise ValueError."""
        with pytest.raises(ValueError, match="gate_fidelity_weight must be non-negative"):
            ScoringWeights(gate_fidelity_weight=-1.0)

        with pytest.raises(ValueError, match="connectivity_weight must be non-negative"):
            ScoringWeights(connectivity_weight=-1.0)

        with pytest.raises(ValueError, match="coherence_weight must be non-negative"):
            ScoringWeights(coherence_weight=-1.0)

        with pytest.raises(ValueError, match="queue_weight must be non-negative"):
            ScoringWeights(queue_weight=-1.0)
