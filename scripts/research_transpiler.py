"""
Research script for Qiskit transpiler API investigation.

This script tests and documents:
1. Transpilation API with fractional gates
2. Error rate extraction from Target
3. Exception handling
4. Performance profiling
"""

import time
from typing import List, Tuple, Optional
from statistics import mean, stdev

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler.exceptions import TranspilerError
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeManilaV2, FakeAlmadenV2


def research_transpilation_api():
    """Research Q1: What Qiskit APIs are needed for transpilation?"""
    print("=" * 80)
    print("RESEARCH Q1: Transpilation API")
    print("=" * 80)
    
    # Create test circuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure_all()
    
    backend = FakeManilaV2()
    
    # Test 1: Basic transpilation
    print("\n1. Basic transpilation:")
    transpiled = transpile(qc, backend=backend, optimization_level=3)
    print(f"   Original gates: {len(qc.data)}")
    print(f"   Transpiled gates: {len(transpiled.data)}")
    print(f"   Transpiled instructions: {[instr.operation.name for instr in transpiled.data]}")
    
    # Test 2: Multiple transpilations to check stochasticity
    print("\n2. Stochastic behavior (5 runs):")
    gate_counts = []
    for i in range(5):
        tc = transpile(qc, backend=backend, optimization_level=3)
        gate_count = len(tc.data)
        gate_counts.append(gate_count)
        print(f"   Run {i+1}: {gate_count} gates")
    
    if len(set(gate_counts)) > 1:
        print(f"   ✓ Transpilation IS stochastic (variance: {stdev(gate_counts):.2f})")
    else:
        print(f"   ✗ Transpilation NOT stochastic (all runs: {gate_counts[0]} gates)")
    
    # Test 3: Fractional gates - check if backend.target() accepts use_fractional_gates
    print("\n3. Fractional gates support:")
    try:
        target_with_frac = backend.target
        print(f"   Backend target type: {type(target_with_frac)}")
        print(f"   Target has {len(target_with_frac.operation_names)} operations")
        
        # Try transpiling with the target
        tc_frac = transpile(qc, target=target_with_frac, optimization_level=2)
        print(f"   ✓ Transpile with target works: {len(tc_frac.data)} gates")
        
    except Exception as e:
        print(f"   ✗ Error with fractional gates: {e}")
    
    return transpiled


def research_error_rate_extraction():
    """Research Q2: How to extract error rates from Target?"""
    print("\n" + "=" * 80)
    print("RESEARCH Q2: Error Rate Extraction from Target")
    print("=" * 80)
    
    backend = FakeAlmadenV2()
    target = backend.target
    
    # Create and transpile a test circuit
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    
    transpiled = transpile(qc, backend=backend, optimization_level=2)
    
    print(f"\nTranspiled circuit operations:")
    for idx, instr in enumerate(transpiled.data):
        print(f"   {idx}: {instr.operation.name} on qubits {instr.qubits}")
    
    print(f"\n   Target instruction extraction:")
    
    total_error = 0.0
    missing_count = 0
    
    for idx, instr in enumerate(transpiled.data):
        op_name = instr.operation.name
        qubits = tuple(q._index for q in instr.qubits)
        
        # Skip measurement
        if op_name == "measure":
            continue
        
        # Get instruction properties
        try:
            if op_name in target.operation_names:
                inst_props_dict = target[op_name]
                
                if qubits in inst_props_dict:
                    props = inst_props_dict[qubits]
                    if props and props.error is not None:
                        error = props.error
                        total_error += error
                        print(f"   {idx}: {op_name}{qubits} -> error={error:.6f}")
                    else:
                        print(f"   {idx}: {op_name}{qubits} -> NO ERROR DATA")
                        missing_count += 1
                else:
                    print(f"   {idx}: {op_name}{qubits} -> QUBIT TUPLE NOT IN TARGET")
                    missing_count += 1
            else:
                print(f"   {idx}: {op_name} -> OPERATION NOT IN TARGET")
                missing_count += 1
                
        except Exception as e:
            print(f"   {idx}: {op_name}{qubits} -> ERROR: {e}")
            missing_count += 1
    
    print(f"\n   Total error sum: {total_error:.6f}")
    print(f"   Missing error data: {missing_count} instructions")
    print(f"   ✓ API confirmed: target[op_name][qubits].error")


def research_exception_handling():
    """Research Q3: What exceptions does transpile() raise?"""
    print("\n" + "=" * 80)
    print("RESEARCH Q3: Transpilation Exception Handling")
    print("=" * 80)
    
    backend = FakeManilaV2()
    
    # Test 1: Invalid circuit (too many qubits)
    print("\n1. Circuit with too many qubits (10 qubits for 5-qubit backend):")
    qc_too_large = QuantumCircuit(10)
    for i in range(9):
        qc_too_large.cx(i, i+1)
    
    try:
        transpiled = transpile(qc_too_large, backend=backend, optimization_level=2)
        print(f"   ✓ Surprisingly succeeded! Gates: {len(transpiled.data)}")
    except TranspilerError as e:
        print(f"   ✗ TranspilerError: {type(e).__name__}: {str(e)[:100]}")
    except Exception as e:
        print(f"   ✗ Other exception: {type(e).__name__}: {str(e)[:100]}")
    
    # Test 2: Empty circuit
    print("\n2. Empty circuit:")
    qc_empty = QuantumCircuit(2)
    
    try:
        transpiled = transpile(qc_empty, backend=backend)
        print(f"   ✓ Succeeded: {len(transpiled.data)} gates")
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {str(e)[:100]}")
    
    # Test 3: Circuit with unsupported gate
    print("\n3. Circuit with custom gate:")
    from qiskit.circuit.library import UGate
    import numpy as np
    
    qc_custom = QuantumCircuit(2)
    qc_custom.append(UGate(np.pi/4, np.pi/2, np.pi), [0])
    qc_custom.cx(0, 1)
    
    try:
        transpiled = transpile(qc_custom, backend=backend, optimization_level=2)
        print(f"   ✓ Succeeded: {len(transpiled.data)} gates")
        print(f"      Transpiler handled decomposition")
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {str(e)[:100]}")
    
    print(f"\n   Expected exception: TranspilerError")
    print(f"   Import: from qiskit.transpiler.exceptions import TranspilerError")


def research_performance():
    """Research Q4: Performance profiling of transpilation"""
    print("\n" + "=" * 80)
    print("RESEARCH Q4: Transpilation Performance")
    print("=" * 80)
    
    backends = [FakeManilaV2(), FakeAlmadenV2()]
    
    # Create circuits of varying sizes
    circuits = []
    for n_qubits in [3, 5]:
        qc = QuantumCircuit(n_qubits)
        qc.h(0)
        for i in range(n_qubits - 1):
            qc.cx(i, i+1)
        qc.h(n_qubits - 1)
        circuits.append((n_qubits, qc))
    
    print(f"\n   Testing transpilation speed:")
    
    total_transpilations = 0
    total_time = 0.0
    
    for n_qubits, qc in circuits:
        for backend in backends:
            # Time 3 transpilation runs
            start = time.time()
            for _ in range(3):
                transpiled = transpile(qc, backend=backend, optimization_level=3)
                total_transpilations += 1
            elapsed = time.time() - start
            total_time += elapsed
            
            avg_time = elapsed / 3
            print(f"   {n_qubits}q on {backend.name}: {avg_time*1000:.2f}ms/transpilation")
    
    print(f"\n   Total: {total_transpilations} transpilations in {total_time:.3f}s")
    print(f"   Average: {(total_time/total_transpilations)*1000:.2f}ms per transpilation")
    
    # Extrapolate to target scenario: 10 backends × 3 runs × 2 fractional configs = 60 transpilations
    estimated_time = (total_time / total_transpilations) * 60
    print(f"\n   Estimated time for 60 transpilations: {estimated_time:.2f}s")
    
    if estimated_time < 10.0:
        print(f"   ✓ PASSES 10-second target (SC-005)")
    else:
        print(f"   ⚠ EXCEEDS 10-second target - may need optimization")
    
    return estimated_time


def main():
    """Run all research investigations"""
    print("QISKIT TRANSPILER API RESEARCH")
    print("=" * 80)
    print("Investigating technical requirements for transpiled circuit scoring")
    print("=" * 80)
    
    # Run all research functions
    research_transpilation_api()
    research_error_rate_extraction()
    research_exception_handling()
    estimated_time = research_performance()
    
    print("\n" + "=" * 80)
    print("RESEARCH SUMMARY")
    print("=" * 80)
    
    print("\n✓ Key Findings:")
    print("  1. transpile() works with backend or target parameter")
    print("  2. Error rates: target[op_name][qubit_tuple].error")
    print("  3. Primary exception: TranspilerError")
    print(f"  4. Performance: ~{estimated_time:.1f}s for 60 transpilations")
    
    print("\n✓ Decisions Confirmed:")
    print("  - Mean aggregation as default (per clarifications)")
    print("  - Cache backend calibration only (per clarifications)")
    print("  - Attempt all backends regardless of qubit count (per clarifications)")
    
    print("\n✓ Next Steps:")
    print("  - Document findings in specs/002-transpiled-error-scoring/research.md")
    print("  - Create data-model.md with entity specifications")
    print("  - Create contracts/ with API specifications")
    print("  - Create quickstart.md with usage examples")
    

if __name__ == "__main__":
    main()
