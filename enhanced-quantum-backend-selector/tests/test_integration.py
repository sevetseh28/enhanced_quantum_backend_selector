"""
Integration tests for end-to-end workflows.

Tests complete workflows with multiple backend types and real scenarios.
"""

import pytest
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import GenericBackendV2

from enhanced_quantum_backend_selector import BackendSelector, ScoringWeights


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_with_aer_simulators(self):
        """Test backend selection with Qiskit Aer simulators."""
        backends = [AerSimulator()]
        selector = BackendSelector(backends)

        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure_all()

        recommendations = selector.rank_backends(qc)
        assert len(recommendations) > 0
        assert recommendations[0].rank == 1

    def test_with_fake_backends(self):
        """Test backend selection with fake provider backends."""
        backends = [
            GenericBackendV2(num_qubits=5, seed=100),
            GenericBackendV2(num_qubits=7, seed=101),
        ]
        selector = BackendSelector(backends)

        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        recommendations = selector.rank_backends(qc)
        assert len(recommendations) == 2
        assert all("generic" in r.backend.name.lower() for r in recommendations)

    def test_end_to_end_workflow(self):
        """Test complete selection workflow from circuit to backend."""
        backends = [GenericBackendV2(num_qubits=5, seed=102)]
        selector = BackendSelector(backends)

        # Create circuit
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        # Select best backend
        best = selector.select_backend(qc)

        # Verify recommendation structure
        assert best.backend is not None
        assert best.score_data is not None
        assert best.metrics is not None
        assert best.rank == 1
        assert best.score_data.backend == best.backend.name

    def test_missing_calibration_data(self):
        """Test graceful handling of missing calibration data."""
        # AerSimulator has minimal calibration data
        backends = [AerSimulator()]
        selector = BackendSelector(backends)

        qc = QuantumCircuit(5)
        for i in range(4):
            qc.cx(i, i + 1)
        qc.measure_all()

        # Should not raise exceptions even with missing data
        recommendations = selector.rank_backends(qc)
        assert len(recommendations) > 0
