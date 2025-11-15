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
        check_qubit_count: bool = True,
        check_gate_support: bool = True,
        check_error_rates: bool = True,
        check_connectivity: bool = True,
        check_coherence_times: bool = True,
        check_queue_depth: bool = True,
    ) -> CircuitScore:
        """
        Score this backend for a specific circuit using multiple checks.

        Args:
            circuit: The quantum circuit to score against
            check_qubit_count: Whether to check if backend has enough qubits
            check_gate_support: Whether to check native gate support
            check_error_rates: Whether to evaluate error rates
            check_connectivity: Whether to evaluate qubit connectivity
            check_coherence_times: Whether to evaluate coherence times
            check_queue_depth: Whether to evaluate queue availability

        Returns:
            CircuitScore containing compatibility and scoring information
        """
        score_data = CircuitScore(
            backend=self.backend.name,
            compatible=True,
            reasons=[],
            score=100.0,  # Start with perfect score
        )

        # Run checks based on enabled flags
        if check_qubit_count:
            if not self._check_qubit_count(circuit, score_data):
                return score_data  # Incompatible, return early

        if check_gate_support:
            self._check_gate_support(circuit, score_data)

        if check_error_rates:
            self._check_error_rates(circuit, score_data)

        if check_connectivity:
            self._check_connectivity(circuit, score_data)

        if check_coherence_times:
            self._check_coherence_times(circuit, score_data)

        if check_queue_depth:
            self._check_queue_depth(circuit, score_data)

        return score_data

    def _check_qubit_count(self, circuit: QuantumCircuit, score_data: CircuitScore) -> bool:
        """
        Check if backend has enough qubits for the circuit.

        Args:
            circuit: The quantum circuit
            score_data: Score data to update

        Returns:
            True if compatible, False otherwise
        """
        if self.backend.num_qubits is not None:
            if self.backend.num_qubits < circuit.num_qubits:
                score_data.compatible = False
                score_data.reasons.append(
                    f"Insufficient qubits: need {circuit.num_qubits}, have {self.backend.num_qubits}"
                )
                score_data.score = 0
                return False
        return True

    def _check_gate_support(self, circuit: QuantumCircuit, score_data: CircuitScore) -> None:
        """
        Check native gate support and penalize for unsupported gates.

        Args:
            circuit: The quantum circuit
            score_data: Score data to update
        """
        circuit_gates = set(circuit.count_ops().keys()) - {"barrier"}
        backend_gates = set(self.target.operation_names)
        unsupported = circuit_gates - backend_gates

        if unsupported:
            # Penalize for gates that need transpilation
            penalty = len(unsupported) * 5  # 5 points per unsupported gate
            score_data.score -= penalty
            score_data.reasons.append(
                f"Unsupported gates (will transpile): {unsupported} (-{penalty} points)"
            )
        else:
            score_data.reasons.append("All gates natively supported (+10 points)")
            score_data.score += 10

    def _check_error_rates(self, circuit: QuantumCircuit, score_data: CircuitScore) -> None:
        """
        Evaluate backend based on gate and readout error rates.

        Args:
            circuit: The quantum circuit
            score_data: Score data to update
        """
        # Two-qubit gate errors
        if self.metrics.avg_2q_error is not None:
            # Lower error = higher score
            # Scale: 1% error = -10 points, 0.1% error = -1 point
            error_penalty = self.metrics.avg_2q_error * 1000
            score_data.score -= error_penalty
            score_data.reasons.append(
                f"2Q error rate: {self.metrics.avg_2q_error*100:.4f}% (-{error_penalty:.1f} points)"
            )

        # Readout errors
        if self.metrics.avg_readout_error is not None:
            # Readout errors weighted less heavily
            error_penalty = self.metrics.avg_readout_error * 200
            score_data.score -= error_penalty
            score_data.reasons.append(
                f"Readout error: {self.metrics.avg_readout_error*100:.3f}% (-{error_penalty:.1f} points)"
            )

    def _check_connectivity(self, circuit: QuantumCircuit, score_data: CircuitScore) -> None:
        """
        Evaluate backend connectivity for circuits with two-qubit gates.

        Args:
            circuit: The quantum circuit
            score_data: Score data to update
        """
        # Count two-qubit gates in circuit
        two_q_count = sum(
            count
            for gate, count in circuit.count_ops().items()
            if gate in ["cx", "cz", "cy", "ecr", "cphase"]
        )

        if two_q_count > 0 and self.metrics.connectivity_ratio is not None:
            # Better connectivity = fewer SWAP gates needed
            connectivity_bonus = self.metrics.connectivity_ratio * 10
            score_data.score += connectivity_bonus
            score_data.reasons.append(
                f"Connectivity: {self.metrics.connectivity_ratio:.2%} (+{connectivity_bonus:.1f} points)"
            )

    def _check_coherence_times(self, circuit: QuantumCircuit, score_data: CircuitScore) -> None:
        """
        Evaluate coherence times for deep circuits.

        Args:
            circuit: The quantum circuit
            score_data: Score data to update
        """
        if circuit.depth() > 10 and self.metrics.avg_t1 is not None:
            # Deeper circuits benefit from longer coherence
            # Scale: 100μs T1 = +5 points, 200μs T1 = +10 points
            coherence_bonus = (self.metrics.avg_t1 * 1e6) / 20
            score_data.score += coherence_bonus
            score_data.reasons.append(
                f"T1 coherence: {self.metrics.avg_t1*1e6:.1f}μs (+{coherence_bonus:.1f} points)"
            )

    def _check_queue_depth(self, circuit: QuantumCircuit, score_data: CircuitScore) -> None:
        """
        Evaluate backend availability based on queue depth.

        Args:
            circuit: The quantum circuit
            score_data: Score data to update
        """
        if self.metrics.pending_jobs is not None:
            # Penalize based on queue depth
            # 0 jobs = +10, 50 jobs = 0, 100+ jobs = -10
            queue_score = 10 - (self.metrics.pending_jobs / 5)
            score_data.score += queue_score
            score_data.reasons.append(
                f"Queue depth: {self.metrics.pending_jobs} jobs ({queue_score:+.1f} points)"
            )
