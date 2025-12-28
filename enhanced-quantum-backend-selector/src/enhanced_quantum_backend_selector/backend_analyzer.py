"""
Backend analysis and scoring module.

This module provides tools for analyzing quantum backends and scoring circuits.
"""

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.circuit_scorer import CircuitScorer
from enhanced_quantum_backend_selector.models import CircuitScore


class BackendAnalyzer:
    """Analyzes quantum backends and scores circuits"""

    def __init__(self, backend: BackendV2):
        self.backend = backend
        self.target = backend.target

    def score_for_circuit(
        self,
        circuit: QuantumCircuit,
    ) -> CircuitScore:
        """
        Score this backend for a specific circuit based on qubit errors.

        Args:
            circuit: The quantum circuit to score against (should be transpiled)

        Returns:
            CircuitScore containing compatibility and scoring information
        """
        scorer = CircuitScorer(self.backend)
        return scorer.score_circuit(circuit)
