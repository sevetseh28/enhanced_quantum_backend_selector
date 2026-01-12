"""Example script demonstrating benchmarking capabilities.

This example shows how to use the benchmark circuits and run benchmarks
to evaluate the Enhanced Quantum Backend Selector.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))



from benchmarks.circuits.benchmark_circuits import (
    create_bernstein_vazirani_circuit,
    create_ghz_circuit,
    create_lucj_ansatz,
    create_qaoa_circuit,
)
from benchmarks.mock_backends import get_all_mock_backends, get_backend_info
from enhanced_quantum_backend_selector import BackendSelector


def main() -> None:
    """Run benchmark examples."""
    print("=" * 70)
    print("Benchmark Circuits Example")
    print("=" * 70)
    print()

    # Create mock backends representing real IBM processors
    print("Creating mock backends (representing real IBM processors)...")
    backends = get_all_mock_backends()
    print(f"  Available backends: {len(backends)}")
    for backend in backends:
        info = get_backend_info(backend)
        print(f"    • {info['name']}: {backend.num_qubits} qubits")
    print()

    # Initialize selector
    selector = BackendSelector(backends)

    # Example 1: GHZ Circuit
    print("-" * 70)
    print("Example 1: GHZ Circuit Benchmarking")
    print("-" * 70)
    ghz = create_ghz_circuit(5)
    print(f"Circuit: {ghz.num_qubits} qubits, depth {ghz.depth()}")

    rec = selector.select_backend(ghz)
    print(f"Best backend: {rec.backend.name}")
    print(f"Expected error: {-rec.score_data.score * 100:.3f}%")
    print()

    # Example 2: Bernstein-Vazirani
    print("-" * 70)
    print("Example 2: Bernstein-Vazirani Algorithm")
    print("-" * 70)
    bv = create_bernstein_vazirani_circuit(5)
    print(f"Circuit: {bv.num_qubits} qubits, depth {bv.depth()}")

    rec = selector.select_backend(bv)
    print(f"Best backend: {rec.backend.name}")
    print(f"Expected error: {-rec.score_data.score * 100:.3f}%")
    print()

    # Example 3: LUCJ Ansatz for Chemistry
    print("-" * 70)
    print("Example 3: LUCJ Ansatz (Chemistry)")
    print("-" * 70)
    lucj = create_lucj_ansatz(4, n_reps=1)
    print(f"Circuit: {lucj.num_qubits} qubits, depth {lucj.depth()}")

    rec = selector.select_backend(lucj)
    print(f"Best backend: {rec.backend.name}")
    print(f"Expected error: {-rec.score_data.score * 100:.3f}%")
    print()

    # Example 4: QAOA for Optimization
    print("-" * 70)
    print("Example 4: QAOA (Optimization)")
    print("-" * 70)
    qaoa = create_qaoa_circuit(4, num_layers=2)
    print(f"Circuit: {qaoa.num_qubits} qubits, depth {qaoa.depth()}")

    rec = selector.select_backend(qaoa)
    print(f"Best backend: {rec.backend.name}")
    print(f"Expected error: {-rec.score_data.score * 100:.3f}%")
    print()

    # Compare all circuits
    print("=" * 70)
    print("Comparison Across Circuits")
    print("=" * 70)
    circuits = [
        ("GHZ-5", ghz),
        ("BV-5", bv),
        ("LUCJ-4", lucj),
        ("QAOA-4", qaoa),
    ]

    for name, circuit in circuits:
        rec = selector.select_backend(circuit)
        error_pct = -rec.score_data.score * 100
        print(f"{name:15} → {rec.backend.name:25} ({error_pct:6.3f}% error)")

    print()
    print("=" * 70)
    print("Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
