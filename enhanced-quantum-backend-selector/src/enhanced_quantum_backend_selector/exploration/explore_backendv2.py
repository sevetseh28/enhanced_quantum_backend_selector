"""
BackendV2 Exploration Examples (Qiskit 2.2)

This script demonstrates how to work with real and simulated backends using
the BackendV2 interface. Essential for understanding what data is available
from actual quantum hardware for intelligent backend selection.

Run this to understand:
1. How to access backend information via BackendV2
2. How to extract Target data from real backends
3. Differences between hardware backends and simulators
4. What metadata is available for selection logic
5. How to handle backends with/without IBM Quantum credentials

Note: Some examples require IBM Quantum credentials. The script will
gracefully handle cases where credentials are not available.
"""

import warnings
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import Sampler
from qiskit.circuit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_ibm_runtime import QiskitRuntimeService

warnings.filterwarnings('ignore')


def explore_simulator_backend():
    """Explore AerSimulator backend capabilities"""
    print("=" * 70)
    print("EXPLORING AERSIMULATOR BACKEND")
    print("=" * 70)
    
    backend = AerSimulator()
    
    print(f"\nBackend name: {backend.name}")
    print(f"Backend version: {backend.backend_version}")
    print(f"Max circuits per job: {backend.max_circuits}")
    
    # Access Target
    target = backend.target
    print(f"\nTarget information:")
    print(f"  Number of qubits: {target.num_qubits} (None = variable size)")
    print(f"  Number of operations: {len(target.operation_names)}")
    print(f"  Description: {target.description}")
    
    # Show supported operations
    print(f"\n  Supported operations ({len(target.operation_names)} total):")
    ops_list = sorted(target.operation_names)
    for i in range(0, len(ops_list), 8):
        print(f"    {', '.join(ops_list[i:i+8])}")
    
    # Check gate properties
    print(f"\n  Gate properties:")
    if 'cx' in target.operation_names:
        cx_qargs = target.qargs_for_operation_name('cx')
        if cx_qargs:
            sample_qargs = list(cx_qargs)[0]
            props = target['cx'].get(sample_qargs)
            if props:
                print(f"    CX error: {props.error}")
                print(f"    CX duration: {props.duration}")
            else:
                print(f"    CX properties: Available globally (no specific error/duration)")
        else:
            print(f"    CX properties: None (simulator - perfect gates)")
    
    # Connectivity
    coupling_map = target.build_coupling_map()
    if coupling_map:
        print(f"\n  Coupling map: {coupling_map}")
    else:
        print(f"\n  Coupling map: None (fully connected)")
    
    # Qubit properties
    if target.qubit_properties:
        print(f"\n  Qubit properties: {len(target.qubit_properties)} qubits")
    else:
        print(f"\n  Qubit properties: None (simulator)")
    
    return backend


def explore_fake_backend():
    """
    Explore a fake backend (simulates real hardware).
    These are useful for testing without consuming real quantum resources.
    """
    print("\n" + "=" * 70)
    print("EXPLORING FAKE BACKEND (Simulated Real Hardware)")
    print("=" * 70)
    
    # Create a fake 5-qubit backend
    backend = GenericBackendV2(num_qubits=5)
    
    print(f"\nBackend name: {backend.name}")
    print(f"Backend version: {backend.backend_version}")
    print(f"Number of qubits: {backend.num_qubits}")
    print(f"Max circuits: {backend.max_circuits}")
    
    # Access Target
    target = backend.target
    print(f"\nTarget information:")
    print(f"  Number of qubits: {target.num_qubits}")
    print(f"  Number of operations: {len(target.operation_names)}")
    print(f"  Operations: {sorted(target.operation_names)}")
    
    # Gate properties
    print(f"\n  Gate error rates (sample):")
    for op_name in ['sx', 'rz', 'cx', 'measure'][:3]:
        if op_name in target.operation_names:
            qargs_list = target.qargs_for_operation_name(op_name)
            if qargs_list:
                sample_qargs = list(qargs_list)[0]
                props = target[op_name].get(sample_qargs)
                if props and props.error is not None:
                    print(f"    {op_name} on {sample_qargs}: {props.error*100:.4f}%")
    
    # Connectivity
    coupling_map = target.build_coupling_map()
    if coupling_map:
        edges = coupling_map.get_edges()
        print(f"\n  Coupling map: {len(edges)} edges")
        print(f"    Sample edges: {list(edges)[:5]}...")
    
    # Qubit properties
    if target.qubit_properties:
        print(f"\n  Qubit properties (first 3):")
        for i in range(min(3, len(target.qubit_properties))):
            props = target.qubit_properties[i]
            print(f"    Qubit {i}:")
            if props.t1:
                print(f"      T1: {props.t1*1e6:.2f} μs")
            if props.t2:
                print(f"      T2: {props.t2*1e6:.2f} μs")
            if props.frequency:
                print(f"      Frequency: {props.frequency*1e-9:.4f} GHz")
    
    return backend


def explore_ibm_backend():
    """
    Explore a real IBM Quantum backend (requires credentials).
    This shows what data is available from actual hardware.
    """
    print("\n" + "=" * 70)
    print("EXPLORING IBM QUANTUM BACKEND")
    print("=" * 70)
    
    # Try to get service
    try:
        service = QiskitRuntimeService()
    except Exception as e:
        print(f"\nIBM Quantum credentials not configured.")
        print(f"To configure, run: QiskitRuntimeService.save_account(token='YOUR_TOKEN')")
        print(f"\nError: {e}")
        return None
    
    # Get least busy backend
    print("\nFetching available backends...")
    backends = service.backends(
        filters=lambda b: b.status().operational and b.num_qubits >= 5
    )
    
    if not backends:
        print("No operational backends available")
        return None
    
    # Get first available backend
    backend = backends[0]
    
    print(f"\nBackend: {backend.name}")
    print(f"Backend version: {backend.backend_version}")
    print(f"Number of qubits: {backend.num_qubits}")
    print(f"Max circuits: {backend.max_circuits}")
    
    # Status
    status = backend.status()
    print(f"\nStatus:")
    print(f"  Operational: {status.operational}")
    print(f"  Pending jobs: {status.pending_jobs}")
    print(f"  Status message: {status.status_msg}")
    
    # Target
    target = backend.target
    print(f"\nTarget information:")
    print(f"  Number of qubits: {target.num_qubits}")
    print(f"  Operations: {sorted(target.operation_names)}")
    print(f"  dt: {target.dt * 1e9:.3f} ns" if target.dt else "  dt: Not specified")
    
    # Native gate set
    print(f"\n  Native gates:")
    for op in sorted(target.operation_names):
        if op not in ['measure', 'delay', 'reset']:
            qargs = target.qargs_for_operation_name(op)
            if qargs:
                num_configs = len(list(qargs))
                print(f"    {op}: {num_configs} configurations")
    
    # 2-qubit gate analysis
    print(f"\n  Two-qubit gate analysis:")
    two_q_ops = [op for op in target.operation_names 
                 if any(len(q) == 2 for q in target.qargs_for_operation_name(op))]
    
    for op in two_q_ops:
        qargs_raw = target.qargs_for_operation_name(op)
        if not qargs_raw:
            continue
        qargs_list = [q for q in qargs_raw if len(q) == 2]
        errors = []
        durations = []
        
        for qargs in qargs_list:
            props = target[op].get(qargs)
            if props:
                if props.error is not None:
                    errors.append(props.error)
                if props.duration is not None:
                    durations.append(props.duration)
        
        if errors:
            avg_error = sum(errors) / len(errors)
            print(f"    {op}: avg error = {avg_error*100:.4f}%, {len(qargs_list)} connections")
    
    # Connectivity
    coupling_map = target.build_coupling_map()
    if coupling_map:
        edges = coupling_map.get_edges()
        print(f"\n  Coupling map:")
        print(f"    Total edges: {len(edges)}")
        print(f"    Symmetric: {coupling_map.is_symmetric}")
        
        # Analyze qubit degrees
        degrees = {}
        for q0, q1 in edges:
            degrees[q0] = degrees.get(q0, 0) + 1
        avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0
        print(f"    Average qubit degree: {avg_degree:.2f}")
    
    # Qubit properties
    if target.qubit_properties:
        print(f"\n  Qubit coherence statistics:")
        t1_values = [p.t1 for p in target.qubit_properties if p.t1 is not None]
        t2_values = [p.t2 for p in target.qubit_properties if p.t2 is not None]
        
        if t1_values:
            print(f"    T1: {min(t1_values)*1e6:.2f} - {max(t1_values)*1e6:.2f} μs (avg: {sum(t1_values)/len(t1_values)*1e6:.2f} μs)")
        if t2_values:
            print(f"    T2: {min(t2_values)*1e6:.2f} - {max(t2_values)*1e6:.2f} μs (avg: {sum(t2_values)/len(t2_values)*1e6:.2f} μs)")
    
    # Properties (legacy but still useful)
    try:
        props = backend.properties()
        if props:
            print(f"\n  Calibration data:")
            print(f"    Last update: {props.last_update_date}")
            
            # Sample readout errors
            readout_errors = []
            for i in range(min(5, backend.num_qubits)):
                error = props.readout_error(i)
                readout_errors.append(error)
            
            if readout_errors:
                avg_readout = sum(readout_errors) / len(readout_errors)
                print(f"    Avg readout error (first 5 qubits): {avg_readout*100:.3f}%")
    except:
        print(f"\n  Properties data: Not available")
    
    return backend


def analyze_backend_for_circuit(backend, circuit):
    """
    Analyze how suitable a backend is for a specific circuit.
    This demonstrates the kind of analysis my selector would perform.
    """
    print("\n" + "=" * 70)
    print("CIRCUIT-BACKEND COMPATIBILITY ANALYSIS")
    print("=" * 70)
    
    print(f"\nCircuit properties:")
    print(f"  Qubits: {circuit.num_qubits}")
    print(f"  Depth: {circuit.depth()}")
    print(f"  Gate counts: {circuit.count_ops()}")
    
    print(f"\nBackend: {backend.name}")
    target = backend.target
    
    # Check 1: Qubit count
    print(f"\n1. Qubit requirement:")
    if backend.num_qubits is None:
        print(f"   ✓ Backend supports variable qubit count (simulator)")
    elif backend.num_qubits >= circuit.num_qubits:
        print(f"   ✓ Backend has {backend.num_qubits} qubits (need {circuit.num_qubits})")
    else:
        print(f"   ✗ Backend has only {backend.num_qubits} qubits (need {circuit.num_qubits})")
        return
    
    # Check 2: Gate set compatibility
    print(f"\n2. Gate set compatibility:")
    circuit_gates = set(circuit.count_ops().keys())
    backend_gates = target.operation_names
    
    supported_gates = circuit_gates.intersection(backend_gates)
    unsupported_gates = circuit_gates - backend_gates
    
    print(f"   Supported: {supported_gates}")
    if unsupported_gates:
        print(f"   Unsupported (will be transpiled): {unsupported_gates}")
    else:
        print(f"   ✓ All gates natively supported!")
    
    # Check 3: Expected gate fidelity
    print(f"\n3. Expected circuit fidelity estimation:")
    
    # This is a simplified estimation
    total_error = 0.0
    gate_count = 0
    
    for gate, count in circuit.count_ops().items():
        if gate in target.operation_names:
            qargs_list = target.qargs_for_operation_name(gate)
            if qargs_list:
                # Get average error for this gate type
                errors = []
                for qargs in qargs_list:
                    props = target[gate].get(qargs)
                    if props and props.error is not None:
                        errors.append(props.error)
                
                if errors:
                    avg_error = sum(errors) / len(errors)
                    total_error += avg_error * count
                    gate_count += count
                    print(f"   {gate}: avg error {avg_error*100:.4f}% × {count} = {avg_error*count*100:.4f}%")
    
    if gate_count > 0:
        expected_fidelity = 1.0 - total_error
        print(f"\n   Rough fidelity estimate: {expected_fidelity*100:.2f}%")
        print(f"   (This is simplified - actual fidelity depends on transpilation)")


def compare_backends_side_by_side(backends):
    """
    Compare multiple backends side by side.
    This shows the kind of comparison my selector would make.
    """
    print("\n" + "=" * 70)
    print("BACKEND COMPARISON")
    print("=" * 70)
    
    print(f"\nComparing {len(backends)} backends:\n")
    
    # Create comparison table
    print(f"{'Backend':<20} {'Qubits':<8} {'Ops':<6} {'Avg 2Q Err':<12} {'Connectivity':<15}")
    print("-" * 75)
    
    for backend in backends:
        target = backend.target
        
        # Calculate average 2Q error
        two_q_errors = []
        for op in target.operation_names:
            qargs_list = target.qargs_for_operation_name(op)
            if qargs_list:
                for qargs in qargs_list:
                    if len(qargs) == 2:
                        props = target[op].get(qargs)
                        if props and props.error is not None:
                            two_q_errors.append(props.error)
        
        avg_2q_error = sum(two_q_errors) / len(two_q_errors) if two_q_errors else None
        
        # Connectivity
        coupling_map = target.build_coupling_map()
        if coupling_map:
            edges = coupling_map.get_edges()
            connectivity = f"{len(edges)} edges"
        else:
            connectivity = "Full"
        
        # Print row
        name = backend.name[:19]
        qubits = str(backend.num_qubits) if backend.num_qubits else "var"
        ops = str(len(target.operation_names))
        error_str = f"{avg_2q_error*100:.4f}%" if avg_2q_error else "N/A"
        
        print(f"{name:<20} {qubits:<8} {ops:<6} {error_str:<12} {connectivity:<15}")


def main():
    """Run all BackendV2 exploration examples"""
    print("\n" + "🔬" * 35)
    print("BACKENDV2 EXPLORATION - Qiskit 2.2")
    print("🔬" * 35)
    
    backends = []
    
    # Explore simulator
    sim_backend = explore_simulator_backend()
    if sim_backend:
        backends.append(sim_backend)
    
    # Explore fake backend
    fake_backend = explore_fake_backend()
    if fake_backend:
        backends.append(fake_backend)
    
    # Explore IBM backend (if credentials available)
    ibm_backend = explore_ibm_backend()
    if ibm_backend:
        backends.append(ibm_backend)
    
    # Compare backends if we have multiple
    if len(backends) > 1:
        compare_backends_side_by_side(backends)
    
    # Demonstrate circuit analysis
    if backends:
        print("\n" + "=" * 70)
        print("EXAMPLE: ANALYZING CIRCUIT-BACKEND FIT")
        print("=" * 70)
        
        # Create a sample circuit
        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure_all()
        
        analyze_backend_for_circuit(backends[0], qc)
    
    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)
    print("\nKey Insights:")
    print("1. BackendV2.target is the primary interface for backend capabilities")
    print("2. Simulators have different characteristics (no errors, variable qubits)")
    print("3. Real hardware has detailed calibration data updated regularly")
    print("4. Circuit-backend compatibility involves multiple factors")
    print("5. Intelligent selection requires comparing multiple metrics")
    print("\nNext: Build my intelligent backend selector!")


if __name__ == "__main__":
    main()
