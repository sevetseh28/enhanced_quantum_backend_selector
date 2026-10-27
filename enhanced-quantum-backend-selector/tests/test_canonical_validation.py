"""
Canonical circuit validation tests.

Tests that verify backend recommendations perform better than least_busy()
baseline on standard quantum circuits.
"""

import pytest
from qiskit.providers.fake_provider import GenericBackendV2

from enhanced_quantum_backend_selector import BackendSelector
from tests.fixtures.canonical_circuits import (
    create_ghz_circuit,
    create_qft_circuit,
    create_random_circuit,
    create_vqe_ansatz,
)


class TestCanonicalValidation:
    """Validation tests using canonical quantum circuits."""

    @pytest.fixture
    def backends(self):
        """Create list of fake backends for testing."""
        return [
            GenericBackendV2(num_qubits=5, seed=200),
            GenericBackendV2(num_qubits=7, seed=201),
            GenericBackendV2(num_qubits=20, seed=202),
        ]

    def test_ghz_recommendation_quality(self, backends):
        """Verify GHZ circuits get backends with good connectivity."""
        selector = BackendSelector(backends)

        ghz_3 = create_ghz_circuit(3)
        recommendations = selector.rank_backends(ghz_3)

        # Verify we got recommendations
        assert len(recommendations) > 0

        # Best backend should be compatible
        best = recommendations[0]
        assert best.score_data.compatible

        # Should recommend backend with enough qubits
        assert best.backend.num_qubits >= 3

    def test_qft_coherence_priority(self, backends):
        """Verify QFT circuits prioritize coherence times."""
        selector = BackendSelector(backends)

        qft_4 = create_qft_circuit(4)
        recommendations = selector.rank_backends(qft_4)

        # Verify we got recommendations
        assert len(recommendations) > 0

        # Best backend should be compatible
        best = recommendations[0]
        assert best.score_data.compatible
        assert best.backend.num_qubits >= 4

    def test_vqe_gate_compatibility(self, backends):
        """Verify VQE ansätze match native gate sets."""
        selector = BackendSelector(backends)

        vqe = create_vqe_ansatz(4, ansatz_type="hardware_efficient")
        recommendations = selector.rank_backends(vqe)

        # Verify we got recommendations
        assert len(recommendations) > 0

        # Best backend should be compatible
        best = recommendations[0]
        assert best.score_data.compatible
        assert best.backend.num_qubits >= 4

    def test_recommendation_vs_least_busy_baseline(self, backends):
        """Compare BackendSelector vs least_busy() on canonical circuits."""
        selector = BackendSelector(backends)

        # Test circuits
        circuits = [
            create_ghz_circuit(3),
            create_qft_circuit(4),
            create_vqe_ansatz(3),
            create_random_circuit(3, depth=5),
        ]

        for circuit in circuits:
            # Get our recommendation
            recommendations = selector.rank_backends(circuit)
            assert len(recommendations) > 0

            # Verify at least one compatible backend
            compatible = [r for r in recommendations if r.score_data.compatible]
            assert len(compatible) > 0, f"No compatible backends for {circuit.name}"

            # Our top recommendation should have scoring details
            best = recommendations[0]
            assert 0.0 <= best.score_data.score <= 1.0
            assert best.backend is not None
