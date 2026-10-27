"""
Circuit scoring module.

This module provides tools for scoring quantum backends based on circuit requirements.
"""

from __future__ import annotations

import math

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.models import SKIP_OPERATIONS, CircuitScore


class CircuitScorer:
    """Scores backends for quantum circuits based on transpiled error analysis.

    The score is built from the estimated success probability (ESP) of the circuit,
    the product of ``(1 - error)`` over every gate in the circuit and the readout of
    every qubit it uses. The reported score is ``-(1 - ESP)``, the negative expected
    error, so it lies in ``[-1, 0]`` and higher is better.

    When the backend reports no error for a specific gate/qubit pair, the mean error of
    that operation across the rest of the device is used instead, so missing calibration
    data never makes a backend look better than it is. Operations with no error data
    anywhere on the device contribute nothing and are listed in the score reasons.
    """

    def __init__(self, backend: BackendV2):
        """
        Initialize the circuit scorer.

        Args:
            backend: The backend to score
        """
        self.backend = backend
        self.target = backend.target
        self._mean_errors: dict[str, float | None] = {}

    def score_circuit(
        self,
        circuit: QuantumCircuit,
    ) -> CircuitScore:
        """
        Score this backend for a specific circuit based on gate and readout errors.

        Args:
            circuit: The quantum circuit to score against (should be transpiled)

        Returns:
            CircuitScore containing compatibility and scoring information
        """
        used_qubits = self._get_used_qubits(circuit)
        log_success, missing = self._log_success_probability(circuit, used_qubits)
        expected_error = 1.0 - math.exp(log_success)

        return CircuitScore(
            backend=self.backend.name,
            compatible=True,
            reasons=self._build_score_reasons(used_qubits, log_success, missing),
            score=-expected_error,  # Negative so higher score = lower error
            log_success_probability=log_success,
        )

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

    def _log_success_probability(
        self, circuit: QuantumCircuit, used_qubits: set[int]
    ) -> tuple[float, set[str]]:
        """
        Calculate the log of the estimated success probability of the circuit.

        Accumulates ``log(1 - error)`` for each gate in the circuit, plus the readout
        error of every used qubit. Working in log space avoids underflow on deep circuits.

        Args:
            circuit: The quantum circuit (should be transpiled to backend)
            used_qubits: Physical qubits used by the circuit

        Returns:
            Tuple of (log success probability, names of operations without error data)
        """
        log_success = 0.0
        missing: set[str] = set()

        for instruction in circuit.data:
            op_name = instruction.operation.name

            # Skip non-gate operations
            if op_name in SKIP_OPERATIONS or op_name not in self.target.operation_names:
                continue

            qargs = tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)
            error = self._gate_error(op_name, qargs)
            if error is None:
                missing.add(op_name)
            else:
                log_success += _log_fidelity(error)

        # Add readout errors for all used qubits (once per qubit)
        if "measure" in self.target.operation_names:
            for qubit in used_qubits:
                error = self._gate_error("measure", (qubit,))
                if error is None:
                    missing.add("measure")
                else:
                    log_success += _log_fidelity(error)

        return log_success, missing

    def _gate_error(self, op_name: str, qargs: tuple[int, ...]) -> float | None:
        """Error of an operation on specific qubits, falling back to the device mean."""
        props = self.target[op_name].get(qargs)
        if props is not None and props.error is not None:
            return float(props.error)
        return self._mean_error(op_name)

    def _mean_error(self, op_name: str) -> float | None:
        """Mean reported error of an operation across the device, or None if unknown."""
        if op_name not in self._mean_errors:
            errors = [
                props.error
                for props in self.target[op_name].values()
                if props is not None and props.error is not None
            ]
            self._mean_errors[op_name] = sum(errors) / len(errors) if errors else None
        return self._mean_errors[op_name]

    def _build_score_reasons(
        self, used_qubits: set[int], log_success: float, missing: set[str]
    ) -> list[str]:
        """
        Build human-readable reasons explaining the score.

        Args:
            used_qubits: Set of qubit indices used in the circuit
            log_success: Log of the estimated success probability
            missing: Operations for which the backend reports no error data

        Returns:
            List of reason strings
        """
        if not used_qubits:
            return ["No qubits used in circuit"]

        # Show the probability in scientific notation so deep circuits stay readable
        success = math.exp(log_success)
        success_text = f"{success:.3g}" if success > 0 else f"e^{log_success:.1f}"
        reasons = [
            f"Estimated success probability on {len(used_qubits)} qubit(s): {success_text}",
            f"Used qubit(s): {sorted(used_qubits)}",
        ]
        if missing:
            reasons.append(f"No error data for: {sorted(missing)}")
        return reasons


def _log_fidelity(error: float) -> float:
    """Log of ``1 - error``, clamped so an error of 1 doesn't raise."""
    return math.log(max(1.0 - error, 1e-300))
