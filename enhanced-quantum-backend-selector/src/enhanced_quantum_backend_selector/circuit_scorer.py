"""
Circuit scoring module.

This module provides tools for scoring quantum backends based on circuit requirements.
"""

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.models import BackendMetrics, CircuitScore


class CircuitScorer:
    """Scores backends for specific quantum circuits using multiple criteria"""

    def __init__(self, backend: BackendV2, metrics: BackendMetrics):
        """
        Initialize the circuit scorer.

        Args:
            backend: The backend to score
            metrics: Pre-extracted metrics for the backend
        """
        self.backend = backend
        self.metrics = metrics
        self.target = backend.target

    def score_circuit(
        self,
        circuit: QuantumCircuit,
    ) -> CircuitScore:
        """
        Score this backend for a specific circuit based on qubit errors.

        The score is calculated by summing up the error rates of all qubits
        used in the circuit. Lower total error = better score.

        Args:
            circuit: The quantum circuit to score against (should be transpiled)

        Returns:
            CircuitScore containing compatibility and scoring information
        """
        score_data = CircuitScore(
            backend=self.backend.name,
            compatible=True,
            reasons=[],
            score=0.0,  # Start with zero, will be set to total error
        )

        # Calculate total error from qubits used in the circuit
        self._calculate_qubit_errors(circuit, score_data)

        return score_data

    def _calculate_qubit_errors(self, circuit: QuantumCircuit, score_data: CircuitScore) -> None:
        """
        Calculate total error from qubits used in the circuit.

        Sums up single-qubit, two-qubit, and readout errors for all qubits
        that are used in the circuit. Lower total error = better backend.

        Args:
            circuit: The quantum circuit (should be transpiled to backend)
            score_data: Score data to update
        """
        # Get the set of qubits used in the circuit
        used_qubits = set()
        for instruction in circuit.data:
            for qubit in instruction.qubits:
                used_qubits.add(circuit.find_bit(qubit).index)

        if not used_qubits:
            score_data.reasons.append("No qubits used in circuit")
            return

        total_error = 0.0

        # Sum single-qubit gate errors for used qubits
        for op_name in self.target.operation_names:
            if op_name in ["measure", "delay", "reset"]:
                continue
            qargs_list = self.target.qargs_for_operation_name(op_name)
            if not qargs_list:
                continue
            for qargs in qargs_list:
                if len(qargs) == 1 and qargs[0] in used_qubits:
                    props = self.target[op_name].get(qargs)
                    if props and props.error is not None:
                        total_error += props.error

        # Sum two-qubit gate errors for used qubit pairs
        for op_name in self.target.operation_names:
            qargs_list = self.target.qargs_for_operation_name(op_name)
            if not qargs_list:
                continue
            for qargs in qargs_list:
                if len(qargs) == 2:
                    if qargs[0] in used_qubits and qargs[1] in used_qubits:
                        props = self.target[op_name].get(qargs)
                        if props and props.error is not None:
                            total_error += props.error

        # Sum readout errors for used qubits
        if "measure" in self.target.operation_names:
            qargs_list = self.target.qargs_for_operation_name("measure")
            if qargs_list:
                for qargs in qargs_list:
                    if len(qargs) == 1 and qargs[0] in used_qubits:
                        props = self.target["measure"].get(qargs)
                        if props and props.error is not None:
                            total_error += props.error

        # Store the total error as the score (lower is better)
        # We use negative score so higher score = lower error
        score_data.score = -total_error
        score_data.reasons.append(
            f"Total error on {len(used_qubits)} qubits: {total_error*100:.6f}%"
        )
        score_data.reasons.append(f"Used qubits: {sorted(used_qubits)}")
