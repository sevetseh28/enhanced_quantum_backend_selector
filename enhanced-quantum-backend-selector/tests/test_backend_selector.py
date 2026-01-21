"""
Unit tests for BackendSelector class.

Tests cover initialization, ranking, selection, caching, and error handling.
"""

import pytest
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from enhanced_quantum_backend_selector import (
    BackendRecommendation,
    BackendSelector,
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
