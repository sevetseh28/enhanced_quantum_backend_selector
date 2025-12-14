"""
Circuit scoring module.

This module provides tools for scoring quantum backends based on circuit requirements.
"""

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.models import BackendMetrics, CircuitScore


class CircuitScorer:
    """Scores backends for quantum circuits based on transpiled error analysis."""

    # Operations to skip when calculating gate errors (non-gate operations)
    SKIP_OPERATIONS = frozenset(["measure", "delay", "reset"])

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
        # Get used qubits and calculate total error
        used_qubits = self._get_used_qubits(circuit)
        total_error = self._calculate_total_error(circuit, used_qubits)

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

    def _calculate_total_error(self, circuit: QuantumCircuit, used_qubits: set[int]) -> float:
        """
        Calculate total error from qubits used in the circuit.

        Sums up single-qubit, two-qubit, and readout errors for all qubits
        that are used in the circuit.

        Args:
            circuit: The quantum circuit (should be transpiled to backend)
            used_qubits: Set of qubit indices used in the circuit

        Returns:
            Total error rate (sum of all error sources)
        """
        if not used_qubits:
            return 0.0

        total_error = 0.0
        total_error += self._sum_single_qubit_errors(used_qubits)
        total_error += self._sum_two_qubit_errors(used_qubits)
        total_error += self._sum_readout_errors(used_qubits)
        return total_error

    def _sum_single_qubit_errors(self, used_qubits: set[int]) -> float:
        """Sum single-qubit gate errors for used qubits."""
        error_sum = 0.0

        for op_name in self.target.operation_names:
            if op_name in self.SKIP_OPERATIONS:
                continue

            qargs_list = self.target.qargs_for_operation_name(op_name)
            if not qargs_list:
                continue

            for qargs in qargs_list:
                if len(qargs) != 1 or qargs[0] not in used_qubits:
                    continue

                props = self.target[op_name].get(qargs)
                if props and props.error is not None:
                    error_sum += props.error

        return error_sum

    def _sum_two_qubit_errors(self, used_qubits: set[int]) -> float:
        """Sum two-qubit gate errors for used qubit pairs."""
        error_sum = 0.0

        for op_name in self.target.operation_names:
            qargs_list = self.target.qargs_for_operation_name(op_name)
            if not qargs_list:
                continue

            for qargs in qargs_list:
                if len(qargs) != 2:
                    continue
                if qargs[0] not in used_qubits or qargs[1] not in used_qubits:
                    continue

                props = self.target[op_name].get(qargs)
                if props and props.error is not None:
                    error_sum += props.error

        return error_sum

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
            f"Total error on {len(used_qubits)} qubits: {total_error * 100:.6f}%",
            f"Used qubits: {sorted(used_qubits)}",
        ]
