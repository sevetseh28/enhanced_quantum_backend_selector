"""
Backend analysis and scoring module.

This module provides tools for analyzing quantum backends and extracting metrics.
"""

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2

from enhanced_quantum_backend_selector.exploration.circuit_scorer import CircuitScorer
from enhanced_quantum_backend_selector.models import BackendMetrics, CircuitScore


class BackendAnalyzer:
    """Analyzes and extracts key metrics from backends for comparison"""

    def __init__(self, backend: BackendV2):
        self.backend = backend
        self.target = backend.target
        self._metrics: BackendMetrics | None = None

    def extract_metrics(self) -> BackendMetrics:
        """Extract all relevant metrics from backend"""
        if self._metrics:
            return self._metrics

        metrics = BackendMetrics(
            name=self.backend.name,
            num_qubits=self.backend.num_qubits,
            max_circuits=self.backend.max_circuits,
        )

        # Operation metrics
        metrics.num_operations = len(self.target.operation_names)
        metrics.operations = list(self.target.operation_names)

        # Single-qubit gate errors
        single_q_errors = self._extract_single_qubit_errors()
        if single_q_errors:
            metrics.avg_1q_error = sum(single_q_errors) / len(single_q_errors)
            metrics.max_1q_error = max(single_q_errors)
            metrics.min_1q_error = min(single_q_errors)

        # Two-qubit gate errors
        two_q_errors = self._extract_two_qubit_errors()
        if two_q_errors:
            metrics.avg_2q_error = sum(two_q_errors) / len(two_q_errors)
            metrics.max_2q_error = max(two_q_errors)
            metrics.min_2q_error = min(two_q_errors)

        # Readout errors
        readout_errors = self._extract_readout_errors()
        if readout_errors:
            metrics.avg_readout_error = sum(readout_errors) / len(readout_errors)
            metrics.max_readout_error = max(readout_errors)

        # Coherence times
        if self.target.qubit_properties:
            t1_values = [p.t1 for p in self.target.qubit_properties if p.t1 is not None]
            t2_values = [p.t2 for p in self.target.qubit_properties if p.t2 is not None]

            if t1_values:
                metrics.avg_t1 = sum(t1_values) / len(t1_values)
                metrics.min_t1 = min(t1_values)
                metrics.max_t1 = max(t1_values)

            if t2_values:
                metrics.avg_t2 = sum(t2_values) / len(t2_values)
                metrics.min_t2 = min(t2_values)

        # Connectivity metrics
        coupling_map = self.target.build_coupling_map()
        if coupling_map:
            edges = coupling_map.get_edges()
            metrics.num_edges = len(edges)
            metrics.is_bidirectional = coupling_map.is_symmetric

            if self.backend.num_qubits:
                max_edges = self.backend.num_qubits * (self.backend.num_qubits - 1)
                metrics.connectivity_ratio = len(edges) / max_edges if max_edges > 0 else 0

            # Calculate average qubit degree
            degrees = {}
            for q0, q1 in edges:
                degrees[q0] = degrees.get(q0, 0) + 1
            metrics.avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0

        # Status (for real backends)
        try:
            status = self.backend.status()
            metrics.operational = status.operational
            metrics.pending_jobs = status.pending_jobs
        except:
            pass  # Keep default None values

        self._metrics = metrics
        return metrics

    def _extract_single_qubit_errors(self) -> list[float]:
        """Extract all single-qubit gate errors"""
        errors = []
        for op_name in self.target.operation_names:
            if op_name in ["measure", "delay", "reset"]:
                continue
            qargs_list = self.target.qargs_for_operation_name(op_name)
            if not qargs_list:
                continue
            for qargs in qargs_list:
                if len(qargs) == 1:
                    props = self.target[op_name].get(qargs)
                    if props and props.error is not None:
                        errors.append(props.error)
        return errors

    def _extract_two_qubit_errors(self) -> list[float]:
        """Extract all two-qubit gate errors"""
        errors = []
        for op_name in self.target.operation_names:
            qargs_list = self.target.qargs_for_operation_name(op_name)
            if not qargs_list:
                continue
            for qargs in qargs_list:
                if len(qargs) == 2:
                    props = self.target[op_name].get(qargs)
                    if props and props.error is not None:
                        errors.append(props.error)
        return errors

    def _extract_readout_errors(self) -> list[float]:
        """Extract readout/measurement errors"""
        if "measure" not in self.target.operation_names:
            return []

        errors = []
        qargs_list = self.target.qargs_for_operation_name("measure")
        if not qargs_list:
            return []

        for qargs in qargs_list:
            props = self.target["measure"].get(qargs)
            if props and props.error is not None:
                errors.append(props.error)
        return errors

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
        metrics = self.extract_metrics()
        scorer = CircuitScorer(self.backend, metrics)
        return scorer.score_circuit(circuit)

    def print_summary(self):
        """Print a formatted summary of backend metrics"""
        metrics = self.extract_metrics()

        print(f"\n{'='*70}")
        print(f"Backend: {metrics.name}")
        print(f"{'='*70}")

        print("\nBasic Properties:")
        print(f"  Qubits: {metrics.num_qubits if metrics.num_qubits else 'variable'}")
        print(f"  Operations: {metrics.num_operations}")
        print(
            f"  Max circuits/job: {metrics.max_circuits if metrics.max_circuits else 'unlimited'}"
        )

        if metrics.avg_1q_error is not None:
            print("\nSingle-Qubit Gate Errors:")
            print(f"  Average: {metrics.avg_1q_error*100:.4f}%")
            print(f"  Range: {metrics.min_1q_error*100:.4f}% - {metrics.max_1q_error*100:.4f}%")

        if metrics.avg_2q_error is not None:
            print("\nTwo-Qubit Gate Errors:")
            print(f"  Average: {metrics.avg_2q_error*100:.4f}%")
            print(f"  Range: {metrics.min_2q_error*100:.4f}% - {metrics.max_2q_error*100:.4f}%")

        if metrics.avg_readout_error is not None:
            print("\nReadout Errors:")
            print(f"  Average: {metrics.avg_readout_error*100:.3f}%")
            print(f"  Max: {metrics.max_readout_error*100:.3f}%")

        if metrics.avg_t1 is not None:
            print("\nCoherence Times:")
            print(
                f"  T1: {metrics.avg_t1*1e6:.2f}μs (range: {metrics.min_t1*1e6:.2f} - {metrics.max_t1*1e6:.2f}μs)"
            )
            if metrics.avg_t2:
                print(f"  T2: {metrics.avg_t2*1e6:.2f}μs (min: {metrics.min_t2*1e6:.2f}μs)")

        if metrics.num_edges is not None:
            print("\nConnectivity:")
            print(f"  Edges: {metrics.num_edges}")
            print(f"  Bidirectional: {metrics.is_bidirectional}")
            print(f"  Connectivity ratio: {metrics.connectivity_ratio:.2%}")
            print(f"  Average qubit degree: {metrics.avg_degree:.2f}")
        else:
            print("\nConnectivity: Fully connected")

        if metrics.operational is not None:
            print("\nStatus:")
            print(f"  Operational: {metrics.operational}")
            print(f"  Pending jobs: {metrics.pending_jobs}")
