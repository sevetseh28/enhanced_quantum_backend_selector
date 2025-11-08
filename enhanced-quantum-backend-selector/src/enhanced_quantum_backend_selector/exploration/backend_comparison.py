"""
Backend Comparison Analysis (Qiskit 2.2)

This script provides comprehensive backend comparison functionality to help
understand what metrics are available for intelligent backend selection.

This demonstrates the kind of analysis framework I'll need for my
intelligent backend selector that goes beyond least_busy().

Key Metrics Extracted:
- Gate error rates (1Q, 2Q, readout)
- Connectivity characteristics
- Coherence times (T1, T2)
- Native gate set compatibility
- Queue depth and availability
- Circuit-specific scoring

Run this to understand how to build a multi-factor scoring system.
"""

from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.providers import BackendV2
from qiskit.circuit import QuantumCircuit
from typing import List, Optional
import warnings

from enhanced_quantum_backend_selector.exploration.backend_analyzer import BackendAnalyzer
from enhanced_quantum_backend_selector.models import BackendMetrics, CircuitScore

# Optional import for IBM Quantum access
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
    HAS_IBM_RUNTIME = True
except ImportError:
    QiskitRuntimeService = None
    HAS_IBM_RUNTIME = False

warnings.filterwarnings('ignore')


def compare_backends_table(backends: List[BackendV2]) -> None:
    """Print a comparison table of multiple backends"""
    print("\n" + "="*120)
    print("BACKEND COMPARISON TABLE")
    print("="*120)
    
    # Print header
    print(f"\n{'Backend':<20} {'Qubits':<8} {'Ops':<5} {'1Q Err':<10} {'2Q Err':<10} {'Readout':<10} {'T1 (μs)':<10} {'Queue':<8}")
    print("-"*120)
    
    for backend in backends:
        analyzer = BackendAnalyzer(backend)
        metrics = analyzer.extract_metrics()
        
        name = metrics.name[:19]
        qubits = str(metrics.num_qubits) if metrics.num_qubits else "var"
        ops = str(metrics.num_operations)
        
        err_1q = f"{metrics.avg_1q_error*100:.4f}%" if metrics.avg_1q_error else "N/A"
        err_2q = f"{metrics.avg_2q_error*100:.4f}%" if metrics.avg_2q_error else "N/A"
        err_ro = f"{metrics.avg_readout_error*100:.3f}%" if metrics.avg_readout_error else "N/A"
        t1 = f"{metrics.avg_t1*1e6:.1f}" if metrics.avg_t1 else "N/A"
        queue = str(metrics.pending_jobs) if metrics.pending_jobs is not None else "N/A"
        
        print(f"{name:<20} {qubits:<8} {ops:<5} {err_1q:<10} {err_2q:<10} {err_ro:<10} {t1:<10} {queue:<8}")


def rank_backends_for_circuit(backends: List[BackendV2], circuit: QuantumCircuit) -> None:
    """Rank backends by suitability for a specific circuit"""
    print("\n" + "="*100)
    print(f"BACKEND RANKING FOR CIRCUIT")
    print("="*100)
    
    print(f"\nCircuit properties:")
    print(f"  Qubits: {circuit.num_qubits}")
    print(f"  Depth: {circuit.depth()}")
    print(f"  Gates: {circuit.count_ops()}")
    
    # Score all backends
    scores = []
    for backend in backends:
        analyzer = BackendAnalyzer(backend)
        score_data = analyzer.score_for_circuit(circuit)
        scores.append(score_data)
    
    # Sort by score (descending)
    scores.sort(key=lambda x: x.score, reverse=True)
    
    print(f"\n{'Rank':<6} {'Backend':<20} {'Score':<10} {'Compatible':<12} Details")
    print("-"*100)
    
    for i, score_data in enumerate(scores, 1):
        rank = f"#{i}"
        name = score_data.backend[:19]
        score = f"{score_data.score:.1f}"
        compatible = "✓" if score_data.compatible else "✗"
        
        print(f"{rank:<6} {name:<20} {score:<10} {compatible:<12}")
        
        # Print reasons
        for reason in score_data.reasons[:3]:  # Show top 3 reasons
            print(f"       └─ {reason}")
        if len(score_data.reasons) > 3:
            print(f"       └─ ... and {len(score_data.reasons) - 3} more factors")


def main():
    """Run comprehensive backend comparison examples"""
    print("\n" + "🔬" * 50)
    print("COMPREHENSIVE BACKEND COMPARISON ANALYSIS - Qiskit 2.2")
    print("🔬" * 50)
    
    # Create sample backends
    print("\nCreating sample backends...")
    
    backends = []
    
    # Simulator
    simulator = AerSimulator()
    backends.append(simulator)
    print(f"  ✓ {simulator.name}")
    
    # Fake backends with different sizes
    for size in [5, 7]:
        try:
            fake = GenericBackendV2(num_qubits=size)
            backends.append(fake)
            print(f"  ✓ {fake.name}")
        except Exception as e:
            print(f"  ✗ Could not create {size}-qubit fake backend: {e}")
    
    # Try to get IBM backend
    if HAS_IBM_RUNTIME:
        try:
            service = QiskitRuntimeService()
            ibm_backends = service.backends(
                filters=lambda b: b.status().operational and b.num_qubits >= 5
            )
            if ibm_backends:
                backends.append(ibm_backends[0])
                print(f"  ✓ {ibm_backends[0].name} (IBM Quantum)")
        except Exception as e:
            print(f"  ℹ IBM Quantum not available: {e}")
    else:
        print(f"  ℹ IBM Quantum not available: qiskit_ibm_runtime not installed")
    
    print(f"\nTotal backends to analyze: {len(backends)}")
    
    # Detailed analysis of each backend
    for backend in backends:
        analyzer = BackendAnalyzer(backend)
        analyzer.print_summary()
    
    # Comparison table
    if len(backends) > 1:
        compare_backends_table(backends)
    
    # Circuit-specific ranking
    print("\n" + "="*100)
    print("CIRCUIT-SPECIFIC BACKEND SELECTION")
    print("="*100)
    
    # Example 1: Simple Bell state
    print("\n\nExample 1: Bell State Circuit")
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    bell.measure_all()
    
    rank_backends_for_circuit(backends, bell)
    
    # Example 2: More complex circuit
    print("\n\n" + "="*100)
    print("\nExample 2: Deeper Circuit (GHZ state)")
    ghz = QuantumCircuit(4)
    ghz.h(0)
    for i in range(3):
        ghz.cx(i, i+1)
    ghz.measure_all()
    
    rank_backends_for_circuit(backends, ghz)
    
    print("\n" + "="*100)
    print("ANALYSIS COMPLETE")
    print("="*100)
    
    print("\n📊 Key Insights for Intelligent Backend Selection:")
    print("\n1. Multiple Metrics Required:")
    print("   - Gate error rates (1Q, 2Q, readout)")
    print("   - Connectivity (topology, density)")
    print("   - Coherence times (T1, T2)")
    print("   - Queue status")
    print("   - Native gate support")
    
    print("\n2. Circuit-Dependent Factors:")
    print("   - Shallow circuits: prioritize gate fidelity")
    print("   - Deep circuits: prioritize coherence time")
    print("   - Many 2Q gates: prioritize connectivity")
    print("   - Specific gates: ensure native support")
    
    print("\n3. Trade-offs to Consider:")
    print("   - Queue time vs. hardware quality")
    print("   - Qubit count vs. error rates")
    print("   - Transpilation cost vs. native gates")
    
    print("\n4. Design Recommendations:")
    print("   - Use weighted scoring system (not single metric)")
    print("   - Cache backend metrics (they change slowly)")
    print("   - Consider circuit characteristics in scoring")
    print("   - Allow user to customize weights")
    print("   - Provide explanation for selection")
    
    print("\n🚀 Next Steps The Enhanced Intelligent Selector:")
    print("   1. Define scoring algorithm with weights")
    print("   2. Add transpilation depth estimation")
    print("   3. Include historical success rate data")
    print("   4. Add cost/credit estimation")
    print("   5. Create user preference profiles?")


if __name__ == "__main__":
    main()
