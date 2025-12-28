"""
Circuit scoring module.

This module provides tools for scoring quantum backends based on circuit requirements.
"""

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.models import SKIP_OPERATIONS, CircuitScore


class CircuitScorer:
    """Scores backends for quantum circuits based on transpiled error analysis."""

    def __init__(self, backend: BackendV2):
        """
        Initialize the circuit scorer.

        Args:
            backend: The backend to score
        """
        self.backend = backend
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
        # Calculate total error for the circuit
        total_error = self._calculate_total_error(circuit)

        # Get used qubits for scoring reasons
        used_qubits = self._get_used_qubits(circuit)

        # Create score data with results
        score_data = CircuitScore(
            backend=self.backend.name,
            compatible=True,
            reasons=self._build_score_reasons(used_qubits, total_error),
            score=-total_error,  # Negative so higher score = lower error
        )

        return score_data

    def _get_used_qubits(self, circuit: QuantumCircuit) -> set[int]:
        """
        Extract the set of physical qubits used in the circuit.

        Args:
            circuit: The quantum circuit (should be transpiled to backend)

        Returns:
            Set of qubit indices used in the circuit
        """
        used_qubits = set()
        for instruction in circuit.data:
            for qubit in instruction.qubits:
                used_qubits.add(circuit.find_bit(qubit).index)
        return used_qubits

    def _calculate_total_error(self, circuit: QuantumCircuit) -> float:
        """
        Calculate total error from gates in the circuit.

        Sums up errors for each gate operation in the circuit, plus readout errors
        for all used qubits.

        Args:
            circuit: The quantum circuit (should be transpiled to backend)

        Returns:
            Total error rate (sum of all error sources)
        """
        if not circuit.data:
            return 0.0

        total_error = 0.0

        # Sum errors for each gate operation in the circuit
        for instruction in circuit.data:
            op_name = instruction.operation.name

            # Skip non-gate operations
            if op_name in SKIP_OPERATIONS:
                continue

            # Get the qubits this operation acts on
            qargs = tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)

            # Get error for this specific gate on these qubits
            if op_name in self.target.operation_names:
                props = self.target[op_name].get(qargs)
                if props and props.error is not None:
                    total_error += props.error

        # Add readout errors for all used qubits (once per qubit)
        used_qubits = self._get_used_qubits(circuit)
        total_error += self._sum_readout_errors(used_qubits)

        return total_error

    def _sum_readout_errors(self, used_qubits: set[int]) -> float:
        """Sum readout errors for used qubits."""
        if "measure" not in self.target.operation_names:
            return 0.0

        error_sum = 0.0
        qargs_list = self.target.qargs_for_operation_name("measure")

        if not qargs_list:
            return 0.0

        for qargs in qargs_list:
            if len(qargs) != 1 or qargs[0] not in used_qubits:
                continue

            props = self.target["measure"].get(qargs)
            if props and props.error is not None:
                error_sum += props.error

        return error_sum

    def _build_score_reasons(self, used_qubits: set[int], total_error: float) -> list[str]:
        """
        Build human-readable reasons explaining the score.

        Args:
            used_qubits: Set of qubit indices used in the circuit
            total_error: Total error rate calculated

        Returns:
            List of reason strings
        """
        if not used_qubits:
            return ["No qubits used in circuit"]

        return [
            f"Total error on {len(used_qubits)} qubit(s): {total_error * 100:.6f}%",
            f"Used qubit(s): {sorted(used_qubits)}",
        ]
