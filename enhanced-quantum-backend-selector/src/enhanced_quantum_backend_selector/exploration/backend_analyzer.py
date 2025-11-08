"""
Backend analysis and scoring module.

This module provides tools for analyzing quantum backends and scoring circuits.
"""

from typing import List, Optional, Dict, Any

from qiskit.circuit import QuantumCircuit
from qiskit.transpiler import Target
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
        circuit_gates = set(circuit.count_ops().keys()) - {'barrier'}
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
            score_data.reasons.append(
                "All gates natively supported (+10 points)"
            )
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
            count for gate, count in circuit.count_ops().items()
            if gate in ['cx', 'cz', 'cy', 'ecr', 'cphase']
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


class BackendAnalyzer:
    """Analyzes and extracts key metrics from backends for comparison"""
    
    def __init__(self, backend: BackendV2):
        self.backend = backend
        self.target = backend.target
        self._metrics: Optional[BackendMetrics] = None
    
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
    
    def _extract_single_qubit_errors(self) -> List[float]:
        """Extract all single-qubit gate errors"""
        errors = []
        for op_name in self.target.operation_names:
            if op_name in ['measure', 'delay', 'reset']:
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
    
    def _extract_two_qubit_errors(self) -> List[float]:
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
    
    def _extract_readout_errors(self) -> List[float]:
        """Extract readout/measurement errors"""
        if 'measure' not in self.target.operation_names:
            return []
        
        errors = []
        qargs_list = self.target.qargs_for_operation_name('measure')
        if not qargs_list:
            return []
        
        for qargs in qargs_list:
            props = self.target['measure'].get(qargs)
            if props and props.error is not None:
                errors.append(props.error)
        return errors
    
    def score_for_circuit(
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
        Score this backend for a specific circuit.
        
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
        metrics = self.extract_metrics()
        scorer = CircuitScorer(self.backend, metrics)
        return scorer.score_circuit(
            circuit,
            check_qubit_count=check_qubit_count,
            check_gate_support=check_gate_support,
            check_error_rates=check_error_rates,
            check_connectivity=check_connectivity,
            check_coherence_times=check_coherence_times,
            check_queue_depth=check_queue_depth,
        )
    
    def print_summary(self):
        """Print a formatted summary of backend metrics"""
        metrics = self.extract_metrics()
        
        print(f"\n{'='*70}")
        print(f"Backend: {metrics.name}")
        print(f"{'='*70}")
        
        print(f"\nBasic Properties:")
        print(f"  Qubits: {metrics.num_qubits if metrics.num_qubits else 'variable'}")
        print(f"  Operations: {metrics.num_operations}")
        print(f"  Max circuits/job: {metrics.max_circuits if metrics.max_circuits else 'unlimited'}")
        
        if metrics.avg_1q_error is not None:
            print(f"\nSingle-Qubit Gate Errors:")
            print(f"  Average: {metrics.avg_1q_error*100:.4f}%")
            print(f"  Range: {metrics.min_1q_error*100:.4f}% - {metrics.max_1q_error*100:.4f}%")
        
        if metrics.avg_2q_error is not None:
            print(f"\nTwo-Qubit Gate Errors:")
            print(f"  Average: {metrics.avg_2q_error*100:.4f}%")
            print(f"  Range: {metrics.min_2q_error*100:.4f}% - {metrics.max_2q_error*100:.4f}%")
        
        if metrics.avg_readout_error is not None:
            print(f"\nReadout Errors:")
            print(f"  Average: {metrics.avg_readout_error*100:.3f}%")
            print(f"  Max: {metrics.max_readout_error*100:.3f}%")
        
        if metrics.avg_t1 is not None:
            print(f"\nCoherence Times:")
            print(f"  T1: {metrics.avg_t1*1e6:.2f}μs (range: {metrics.min_t1*1e6:.2f} - {metrics.max_t1*1e6:.2f}μs)")
            if metrics.avg_t2:
                print(f"  T2: {metrics.avg_t2*1e6:.2f}μs (min: {metrics.min_t2*1e6:.2f}μs)")
        
        if metrics.num_edges is not None:
            print(f"\nConnectivity:")
            print(f"  Edges: {metrics.num_edges}")
            print(f"  Bidirectional: {metrics.is_bidirectional}")
            print(f"  Connectivity ratio: {metrics.connectivity_ratio:.2%}")
            print(f"  Average qubit degree: {metrics.avg_degree:.2f}")
        else:
            print(f"\nConnectivity: Fully connected")
        
        if metrics.operational is not None:
            print(f"\nStatus:")
            print(f"  Operational: {metrics.operational}")
            print(f"  Pending jobs: {metrics.pending_jobs}")
