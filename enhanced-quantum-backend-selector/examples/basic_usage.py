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


def print_metric(label: str, value: float | None, format_spec: str = ".2e", unit: str = "") -> None:
    """Print a metric with conditional N/A handling."""
    if value:
        formatted = f"{value:{format_spec}}"
        if unit:
            formatted = f"{formatted} {unit}"
        print(f"    {label:<16}{formatted}")
    else:
        print(f"    {label:<16}N/A")


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

        print("  Backend Properties:")
        print(f"    Num Qubits:     {recommendation.backend.num_qubits}")
        # Get connectivity info from backend
        coupling_map = recommendation.backend.target.build_coupling_map()
        num_edges = len(coupling_map.get_edges()) if coupling_map else 0
        print(f"    Connectivity:   {num_edges} edges")
        # Access qubit properties directly
        if recommendation.backend.target.qubit_properties:
            t1_values = [p.t1 for p in recommendation.backend.target.qubit_properties if p.t1 is not None]
            t2_values = [p.t2 for p in recommendation.backend.target.qubit_properties if p.t2 is not None]
            if t1_values:
                avg_t1 = sum(t1_values) / len(t1_values)
                print_metric("Avg T1 Time:", avg_t1, ".2e", "seconds")
            if t2_values:
                avg_t2 = sum(t2_values) / len(t2_values)
                print_metric("Avg T2 Time:", avg_t2, ".2e", "seconds")
        # Check operational status
        try:
            status = recommendation.backend.status()
            print(f"    Operational:    {status.operational}")
        except Exception:
            pass
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
        coupling_map = rec.backend.target.build_coupling_map()
        num_edges = len(coupling_map.get_edges()) if coupling_map else 0
        print(f"  {rec.rank}. {rec.backend.name}")
        print(f"     Score: {rec.score_data.score:.3f} | "
              f"Qubits: {rec.backend.num_qubits} | "
              f"Edges: {num_edges}")
    print()

    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
