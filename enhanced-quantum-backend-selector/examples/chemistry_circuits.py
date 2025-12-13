"""Chemistry circuit example for Enhanced Quantum Backend Selector.

This example demonstrates:
1. Comparing standard vs fractional gates for chemistry circuits
2. VQE ansatz optimization
3. How fractional gates can improve performance

Note: Fractional gates are a backend-level property. In real usage with IBM Quantum,
you would get both versions: service.backend('name') and service.backend('name', use_fractional_gates=True)
"""

from qiskit import QuantumCircuit
from qiskit.circuit.library import EfficientSU2
from qiskit.providers.fake_provider import GenericBackendV2

from enhanced_quantum_backend_selector import BackendSelector


def main() -> None:
    """Run chemistry circuit examples demonstrating fractional gates detection."""
    print("=" * 70)
    print("Chemistry Circuits - Fractional Gates Detection Example")
    print("=" * 70)
    print()

    # Setup backends (in real usage, get both standard and fractional versions)
    print("Setup: Creating test backends...")
    backends = [
        GenericBackendV2(num_qubits=5, seed=200),
        GenericBackendV2(num_qubits=7, seed=201),
        GenericBackendV2(num_qubits=27, seed=202),
    ]
    print(f"  Available backends: {len(backends)}")
    print()

    # Example 1: VQE Ansatz
    print("=" * 70)
    print("Example 1: VQE Ansatz with Fractional Gates Detection")
    print("-" * 70)

    # Create a typical chemistry ansatz
    ansatz = EfficientSU2(num_qubits=4, reps=2, entanglement="linear")
    ansatz.measure_all()

    print(f"  Circuit: {ansatz.num_qubits} qubits, depth {ansatz.depth()}")
    print(f"  Gates: {dict(ansatz.count_ops())}")
    print()

    # The selector detects fractional gates from backend properties
    print("  Selecting best backend (selector detects gate configuration)...")
    selector = BackendSelector(backends)
    rec = selector.select_backend(ansatz)

    error = -rec.score_data.score * 100
    print(f"    Best backend: {rec.backend.name}")
    print(f"    Score: {rec.score_data.score:.6f}")
    print(f"    Expected error: {error:.3f}%")

    # Find which configuration was detected
    gate_config = "unknown"
    for reason in rec.score_data.reasons:
        if "fractional" in reason.lower() or "standard" in reason.lower():
            gate_config = reason
            print(f"    {reason}")
    print()

    # Example 2: Compare All Backends
    print("=" * 70)
    print("Example 2: Full Rankings with Gate Configuration Detection")
    print("-" * 70)

    all_rankings = selector.rank_backends(ansatz)

    print(f"\n  Backend Rankings for VQE Ansatz:")
    print("  " + "-" * 66)
    print(f"  {'Rank':<6} {'Backend':<25} {'Score':>12} {'Error %':>10}")
    print("  " + "-" * 66)

    for rec in all_rankings:
        error_pct = -rec.score_data.score * 100
        print(f"  #{rec.rank:<5} {rec.backend.name:<25} "
              f"{rec.score_data.score:>12.6f} {error_pct:>9.3f}%")
    print()

    # Example 3: Custom Chemistry Circuit
    print("=" * 70)
    print("Example 3: Custom Chemistry Circuit")
    print("-" * 70)

    # Create a custom circuit with rotation gates
    custom_qc = QuantumCircuit(3)
    custom_qc.ry(0.5, 0)
    custom_qc.rz(0.3, 1)
    custom_qc.ry(0.7, 2)
    custom_qc.cx(0, 1)
    custom_qc.cx(1, 2)
    custom_qc.ry(-0.5, 0)
    custom_qc.rz(-0.3, 1)
    custom_qc.measure_all()

    print(f"  Circuit: {custom_qc.num_qubits} qubits, depth {custom_qc.depth()}")
    print(f"  Contains rotation gates: RY, RZ")
    print()

    rec_custom = selector.select_backend(custom_qc)
    error_custom = -rec_custom.score_data.score * 100

    print(f"  Best backend: {rec_custom.backend.name}")
    print(f"  Score: {rec_custom.score_data.score:.6f}")
    print(f"  Expected error: {error_custom:.3f}%")

    # Show configuration used
    for reason in rec_custom.score_data.reasons:
        if "fractional" in reason.lower() or "standard" in reason.lower():
            print(f"  {reason}")
    print()

    print("=" * 70)
    print("Chemistry circuit examples completed!")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  \u2022 Selector detects fractional gates from backend properties")
    print("  \u2022 To compare: pass both standard and fractional backend versions")
    print("  \u2022 Get fractional version: service.backend(name, use_fractional_gates=True)")
    print("  \u2022 Particularly beneficial for circuits with many rotation gates")


if __name__ == "__main__":
    main()
