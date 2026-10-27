"""
Unit tests for BackendSelector class.

Tests cover initialization, ranking, selection, caching, and error handling.
"""

import math

import pytest
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke, FakeTorino

from enhanced_quantum_backend_selector import (
    BackendRecommendation,
    BackendSelector,
    CircuitScore,
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


class _Status:
    """Minimal stand-in for qiskit-ibm-runtime's BackendStatus."""

    def __init__(self, operational: bool, status_msg: str) -> None:
        self.operational = operational
        self.status_msg = status_msg


class _OfflineBackend(GenericBackendV2):
    """Generic backend that reports itself as not operational."""

    def status(self) -> _Status:
        return _Status(operational=False, status_msg="maintenance")


class _BrokenBackend(GenericBackendV2):
    """Generic backend whose target can't be read, so transpilation fails."""

    _broken = False

    def __init__(self, num_qubits: int, seed: int) -> None:
        super().__init__(num_qubits=num_qubits, seed=seed)
        self._broken = True

    @property
    def target(self):
        if self._broken:
            raise RuntimeError("calibration data unavailable")
        return super().target


@pytest.fixture
def bell_circuit() -> QuantumCircuit:
    """Create a 2-qubit Bell circuit."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc


class TestCompatibility:
    """Backends that can't run the circuit are ranked last and flagged."""

    def test_too_few_qubits_is_incompatible(self):
        small = GenericBackendV2(num_qubits=2, seed=1)
        large = GenericBackendV2(num_qubits=5, seed=2)
        qc = QuantumCircuit(4)
        qc.h(0)
        qc.cx(0, 3)

        ranked = BackendSelector([small, large]).rank_backends(qc)

        assert ranked[0].backend is large
        assert ranked[1].backend is small
        assert ranked[1].score_data.compatible is False
        assert ranked[1].score_data.score == 0.0
        assert ranked[1].score_data.log_success_probability == float("-inf")
        assert "needs 4 qubits" in ranked[1].score_data.reasons[0]

    def test_non_operational_backend_is_incompatible(self, bell_circuit):
        offline = _OfflineBackend(num_qubits=3, seed=1)

        ranked = BackendSelector([offline]).rank_backends(bell_circuit)

        assert ranked[0].score_data.compatible is False
        assert "not operational (maintenance)" in ranked[0].score_data.reasons[0]

    def test_failing_backend_does_not_hide_others(self, bell_circuit, caplog):
        broken = _BrokenBackend(num_qubits=3, seed=1)
        working = GenericBackendV2(num_qubits=3, seed=2)

        ranked = BackendSelector([broken, working]).rank_backends(bell_circuit)

        assert [r.backend for r in ranked] == [working, broken]
        assert ranked[1].score_data.compatible is False
        assert "calibration data unavailable" in caplog.text

    def test_select_raises_when_nothing_is_compatible(self, bell_circuit):
        selector = BackendSelector([_OfflineBackend(num_qubits=3, seed=1)])

        with pytest.raises(RuntimeError, match="No compatible backends found"):
            selector.select_backend(bell_circuit)

    def test_select_can_return_incompatible_backend(self, bell_circuit):
        selector = BackendSelector([_OfflineBackend(num_qubits=3, seed=1)])

        best = selector.select_backend(bell_circuit, require_compatible=False)

        assert best.score_data.compatible is False

    def test_min_score_filters_backends(self, bell_circuit):
        selector = BackendSelector([GenericBackendV2(num_qubits=3, seed=1)])

        with pytest.raises(RuntimeError, match="minimum score threshold"):
            selector.select_backend(bell_circuit, min_score=1.0)


class TestReproducibility:
    """Seeded selectors produce the same ranking every time."""

    def test_seed_gives_identical_scores(self):
        backends = [FakeTorino(), FakeSherbrooke()]
        qc = QuantumCircuit(5)
        qc.h(0)
        for i in range(4):
            qc.cx(i, i + 1)
        qc.measure_all()

        first = BackendSelector(backends, seed=7).rank_backends(qc)
        second = BackendSelector(backends, seed=7).rank_backends(qc)

        assert [(r.backend.name, r.score_data.score) for r in first] == [
            (r.backend.name, r.score_data.score) for r in second
        ]

    def test_saturated_scores_rank_by_log_success_probability(self, bell_circuit, monkeypatch):
        """On very deep circuits every score underflows to 0; the log success ranks them."""
        worse = GenericBackendV2(num_qubits=3, seed=1)
        better = GenericBackendV2(num_qubits=3, seed=2)
        log_success = {id(worse): -900.0, id(better): -800.0}

        def fake_score(backend, circuit):
            return BackendRecommendation(
                backend=backend,
                score_data=CircuitScore(
                    backend=backend.name,
                    compatible=True,
                    score=0.0,
                    log_success_probability=log_success[id(backend)],
                ),
                rank=0,
            )

        selector = BackendSelector([worse, better])
        monkeypatch.setattr(selector, "_score_single_backend", fake_score)

        ranked = selector.rank_backends(bell_circuit)

        assert [r.backend for r in ranked] == [better, worse]

    def test_scores_are_success_probabilities(self, bell_circuit):
        ranked = BackendSelector([FakeTorino()], seed=1).rank_backends(bell_circuit)
        score_data = ranked[0].score_data

        assert 0.0 < score_data.score < 1.0
        assert score_data.score == pytest.approx(math.exp(score_data.log_success_probability))


def test_log_mean_exp_matches_arithmetic_mean():
    """Runs are averaged as probabilities, so one bad run doesn't dominate."""
    from enhanced_quantum_backend_selector.backend_selector import _log_mean_exp

    values = [math.log(0.5), math.log(0.1), -2000.0]

    assert _log_mean_exp(values) == pytest.approx(math.log((0.5 + 0.1 + 0.0) / 3))
    assert _log_mean_exp([-5000.0, -5001.0]) > -5001.0
    assert _log_mean_exp([float("-inf")]) == float("-inf")
