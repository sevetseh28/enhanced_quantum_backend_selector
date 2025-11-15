"""Basic usage example for Enhanced Quantum Backend Selector.

This example demonstrates:
1. Getting available backends from a provider
2. Creating a simple quantum circuit
3. Selecting the best backend for the circuit
4. Understanding the recommendation results
"""

from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from enhanced_quantum_backend_selector import BackendSelector


def main() -> None:
    """Run basic backend selection example."""
    print("=" * 70)
    print("Enhanced Quantum Backend Selector - Basic Usage")
    print("=" * 70)
    print()

    # Step 1: Get available backends
    # In production, use: service = QiskitRuntimeService()
    #                     backends = service.backends()
    # For this example, we'll use generic fake backends
    print("Step 1: Creating simulated backends...")
    backends = [
        GenericBackendV2(num_qubits=5, seed=42),
        GenericBackendV2(num_qubits=7, seed=43),
        GenericBackendV2(num_qubits=27, seed=44),
    ]
    print(f"  Available backends: {len(backends)}")
    for backend in backends:
        print(f"    - {backend.name} ({backend.num_qubits} qubits)")
    print()

    # Step 2: Create a quantum circuit
    print("Step 2: Creating quantum circuit (GHZ state)...")
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure_all()
    print(f"  Circuit: {qc.num_qubits} qubits, depth {qc.depth()}")
    print()

    # Step 3: Initialize the backend selector
    print("Step 3: Initializing BackendSelector...")
    selector = BackendSelector(backends)
    print(f"  Loaded {len(selector.backends)} backends")
    print()

    # Step 4: Select the best backend
    print("Step 4: Selecting best backend for circuit...")
    try:
        recommendation = selector.select_backend(qc)
        
        print(f"\n✓ Recommended Backend: {recommendation.backend.name}")
        print(f"  Rank: #{recommendation.rank}")
        print(f"  Overall Score: {recommendation.score_data.score:.3f}")
        print(f"  Compatible: {recommendation.score_data.compatible}")
        print()
        
        print("  Backend Metrics:")
        print(f"    Num Qubits:     {recommendation.metrics.num_qubits}")
        print(f"    Connectivity:   {recommendation.metrics.num_edges} edges")
        print(f"    Avg T1 Time:    {recommendation.metrics.avg_t1:.2e} seconds" if recommendation.metrics.avg_t1 else "    Avg T1 Time:    N/A")
        print(f"    Avg T2 Time:    {recommendation.metrics.avg_t2:.2e} seconds" if recommendation.metrics.avg_t2 else "    Avg T2 Time:    N/A")
        print(f"    Readout Error:  {recommendation.metrics.avg_readout_error:.4f}" if recommendation.metrics.avg_readout_error else "    Readout Error:  N/A")
        print(f"    Operational:    {recommendation.metrics.operational}")
        print()
        
        if recommendation.score_data.reasons:
            print("  Selection Reasons:")
            for reason in recommendation.score_data.reasons:
                print(f"    • {reason}")
        print()
        
    except ValueError as e:
        print(f"✗ Error: {e}")
        print()

    # Step 5: Show alternative approach - get top 3 rankings
    print("Step 5: Getting top 3 backend rankings...")
    rankings = selector.rank_backends(qc, top_n=3)
    
    print(f"\nTop {len(rankings)} Backends:")
    print("-" * 70)
    for rec in rankings:
        print(f"  {rec.rank}. {rec.backend.name}")
        print(f"     Score: {rec.score_data.score:.3f} | "
              f"Qubits: {rec.metrics.num_qubits} | "
              f"Edges: {rec.metrics.num_edges or 0}")
    print()

    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
