"""
Circuit scoring module.

This module provides tools for scoring quantum backends based on circuit requirements.
"""

from __future__ import annotations

import math

from qiskit.circuit import Delay, QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.models import SKIP_OPERATIONS, CircuitScore

_SECONDS_PER_UNIT = {"s": 1.0, "ms": 1e-3, "us": 1e-6, "ns": 1e-9, "ps": 1e-12}


class CircuitScorer:
    """Scores backends for quantum circuits based on transpiled error analysis.

    The score is built from the estimated success probability (ESP) of the circuit,
    the product of ``(1 - error)`` over every gate in the circuit, the readout of
    every qubit it uses, and the time each qubit spends idle. The reported score is
    the ESP itself, between 0 and 1: ``0.98`` means a 98% chance the circuit runs
    without error. Higher is better.

    Idle error comes from each qubit's T1/T2 and the time it waits between its first
    and last operation, using gate durations from the backend and an as-late-as-possible
    schedule. A qubit idle for time ``t`` contributes the average infidelity of
    amplitude damping and dephasing, ``1/2 - exp(-t/T1)/6 - exp(-t/T2)/3``. Backends
    without durations or T1/T2 data get no idle error.

    When the backend reports no error for a specific gate/qubit pair, the mean error of
    that operation across the rest of the device is used instead, so missing calibration
    data never makes a backend look better than it is. The same applies to gate
    durations and T1/T2. Operations with no error data anywhere on the device contribute
    nothing and are listed in the score reasons.
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
        self._mean_durations: dict[str, float | None] = {}
        self._mean_coherence: tuple[float, float] | None = None

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
        log_idle, idle_time = self._log_idle_fidelity(circuit)
        log_success += log_idle

        reasons = self._build_score_reasons(used_qubits, log_success, missing)
        if idle_time > 0:
            reasons.append(
                f"Idle time: {idle_time * 1e6:.1f} us in total, "
                f"idle success probability {math.exp(log_idle):.3g}"
            )

        return CircuitScore(
            backend=self.backend.name,
            compatible=True,
            reasons=reasons,
            score=math.exp(log_success),
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

    def _log_idle_fidelity(self, circuit: QuantumCircuit) -> tuple[float, float]:
        """
        Calculate the log of the probability that no qubit decoheres while idle.

        The circuit is scheduled as late as possible by walking it backwards: each
        operation starts once all of its qubits are free, and a barrier lines its qubits
        up. A qubit's idle time is the span from its first to its last operation minus
        the time it spends in operations, so the wait before its first gate (while it
        is still in the ground state) is not counted.

        Args:
            circuit: The quantum circuit (should be transpiled to backend)

        Returns:
            Tuple of (log idle success probability, total idle time in seconds)
        """
        free_at: dict[int, float] = {}
        busy: dict[int, float] = {}
        first: dict[int, float] = {}
        last: dict[int, float] = {}

        for instruction in reversed(circuit.data):
            qargs = tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)
            op_name = instruction.operation.name

            if op_name == "barrier":
                started = [q for q in qargs if q in first]
                if started:
                    sync = max(free_at[q] for q in started)
                    for q in started:
                        free_at[q] = sync
                continue

            start = max(free_at.get(q, 0.0) for q in qargs)
            if op_name == "delay":
                # Explicit delays are idle time, not time spent in an operation
                duration = self._delay_seconds(instruction.operation)
                for q in qargs:
                    if q in first:
                        free_at[q] = start + duration
                continue

            duration = self._duration(op_name, qargs)
            for q in qargs:
                first.setdefault(q, start)
                free_at[q] = last[q] = start + duration
                busy[q] = busy.get(q, 0.0) + duration

        log_idle = 0.0
        total_idle = 0.0
        for qubit, start in first.items():
            idle = last[qubit] - start - busy[qubit]
            coherence = self._coherence(qubit)
            if idle <= 0 or coherence is None:
                continue
            t1, t2 = coherence
            total_idle += idle
            fidelity = 0.5 + math.exp(-idle / t1) / 6 + math.exp(-idle / t2) / 3
            log_idle += math.log(fidelity)

        return log_idle, total_idle

    def _duration(self, op_name: str, qargs: tuple[int, ...]) -> float:
        """Duration of an operation in seconds, falling back to the device mean, or 0."""
        if op_name not in self.target.operation_names:
            return 0.0
        props = self.target[op_name].get(qargs)
        if props is not None and props.duration is not None:
            return float(props.duration)
        if op_name not in self._mean_durations:
            durations = [
                props.duration
                for props in self.target[op_name].values()
                if props is not None and props.duration is not None
            ]
            self._mean_durations[op_name] = sum(durations) / len(durations) if durations else None
        return self._mean_durations[op_name] or 0.0

    def _delay_seconds(self, delay: Delay) -> float:
        """Length of a delay instruction in seconds, or 0 if it can't be converted."""
        if delay.unit == "dt":
            return float(delay.duration) * self.target.dt if self.target.dt else 0.0
        return float(delay.duration) * _SECONDS_PER_UNIT.get(delay.unit, 0.0)

    def _coherence(self, qubit: int) -> tuple[float, float] | None:
        """(T1, T2) of a qubit in seconds, falling back to the device mean, or None."""
        properties = self.target.qubit_properties
        if not properties:
            return None
        props = properties[qubit] if qubit < len(properties) else None
        t1 = getattr(props, "t1", None)
        t2 = getattr(props, "t2", None)
        if t1 and t2:
            return float(t1), float(t2)
        if self._mean_coherence is None:
            pairs = [(p.t1, p.t2) for p in properties if p is not None and p.t1 and p.t2]
            self._mean_coherence = (
                (sum(t1 for t1, _ in pairs) / len(pairs), sum(t2 for _, t2 in pairs) / len(pairs))
                if pairs
                else (0.0, 0.0)
            )
        return self._mean_coherence if self._mean_coherence[0] else None

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
