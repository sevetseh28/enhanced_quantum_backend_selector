"""Advanced usage example for Enhanced Quantum Backend Selector.

This example demonstrates:
1. Comparing multiple backends with transpilation-based scoring
2. Understanding score interpretation (negative error sums)
3. Analyzing top-ranked backends
4. Handling different circuit complexities
"""

from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2

from enhanced_quantum_backend_selector import (
    BackendRecommendation,
    BackendSelector,
)


def print_recommendation(rec: BackendRecommendation, title: str) -> None:
    """Print formatted recommendation details."""
    error_pct = -rec.score_data.score * 100
    print(f"\n  {title}")
    print(f"  Backend:  {rec.backend.name}")
    print(f"  Score:    {rec.score_data.score:.6f} (negative error sum)")
    print(f"  Error:    {error_pct:.3f}%")
    print(f"  Qubits:   {rec.metrics.num_qubits}")
    print(f"  Compatible: {rec.score_data.compatible}")


def main() -> None:
    """Run advanced backend selection examples."""
    print("=" * 70)
    print("Enhanced Quantum Backend Selector - Advanced Usage")
    print("=" * 70)
    print()

    # Setup: Create backends and circuit
    print("Setup: Creating test environment...")
    backends = [
        GenericBackendV2(num_qubits=5, seed=100),
        GenericBackendV2(num_qubits=7, seed=101),
        GenericBackendV2(num_qubits=27, seed=102),
        GenericBackendV2(num_qubits=127, seed=103),
    ]

    # Create a more complex circuit requiring good connectivity
    qc = QuantumCircuit(5)
    qc.h(0)
    for i in range(4):
        qc.cx(i, i + 1)
    qc.barrier()
    for i in range(5):
        qc.rz(0.5, i)
    qc.measure_all()

    print(f"  Circuit: {qc.num_qubits} qubits, depth {qc.depth()}, "
          f"{qc.count_ops().get('cx', 0)} CX gates")
    print(f"  Available backends: {len(backends)}")
    print()

    selector = BackendSelector(backends)

    # Example 1: Get Best Backend
    print("=" * 70)
    print("Example 1: Select Best Backend")
    print("  Uses transpilation-based scoring to find optimal backend")
    print("-" * 70)

    best = selector.select_backend(qc)
    print_recommendation(best, "Best Backend (Rank #1)")
    print()

    # Example 2: Get Top 3 Rankings
    print("=" * 70)
    print("Example 2: Compare Top 3 Backends")
    print("  Shows how backends compare on actual transpiled circuit")
    print("-" * 70)

    top_3 = selector.rank_backends(qc, top_n=3)
    for rec in top_3:
        print_recommendation(rec, f"Rank #{rec.rank}")
    print()

    # Example 3: All Rankings
    print("=" * 70)
    print("Example 3: Full Backend Rankings")
    print("  Complete ranking of all available backends")
    print("-" * 70)

    all_recs = selector.rank_backends(qc)
    print(f"\n  {'Rank':<6} {'Backend':<30} {'Score':>12} {'Error %':>10} {'Qubits':>8}")
    print("  " + "-" * 72)
    for rec in all_recs:
        error_pct = -rec.score_data.score * 100
        print(f"  #{rec.rank:<5} {rec.backend.name:<30} "
              f"{rec.score_data.score:>12.6f} {error_pct:>9.3f}% {rec.metrics.num_qubits:>8}")
    print()

    # Example 4: Understanding Score Differences
    print("=" * 70)
    print("Example 4: Score Interpretation")
    print("  Scores are negative error sums - higher (less negative) is better")
    print("-" * 70)

    print(f"\n  Best backend: {all_recs[0].backend.name}")
    print(f"    Score: {all_recs[0].score_data.score:.6f}")
    print(f"    Expected error: {-all_recs[0].score_data.score * 100:.3f}%")
    print(f"\n  Worst backend: {all_recs[-1].backend.name}")
    print(f"    Score: {all_recs[-1].score_data.score:.6f}")
    print(f"    Expected error: {-all_recs[-1].score_data.score * 100:.3f}%")

    improvement = (all_recs[-1].score_data.score - all_recs[0].score_data.score)
    improvement_pct = (-improvement / -all_recs[-1].score_data.score) * 100
    print(f"\n  Error reduction by choosing best: {improvement_pct:.1f}%")
    print()

    # Example 5: Compare all strategies side-by-side
    print("=" * 70)
    print("Example 5: Strategy Comparison Summary")
    print()

    # Example 5: Minimum score filtering
    print("=" * 70)
    print("Example 5: Minimum Score Filtering")
    print("  Require backends to meet quality threshold")
    print("-" * 70)

    min_score = -0.05  # Require less than 5% expected error
    print(f"\n  Minimum acceptable score: {min_score} (< 5% error)")
    print("  Note: Scores are negative - higher (less negative) is better")

    try:
        filtered_rec = selector.select_backend(qc, min_score=min_score)
        error_pct = -filtered_rec.score_data.score * 100
        print(f"  ✓ Found backend: {filtered_rec.backend.name} "
              f"(score: {filtered_rec.score_data.score:.6f}, error: {error_pct:.3f}%)")
    except RuntimeError as e:
        print(f"  ✗ No backends met minimum score: {e}")
    print()

    # Example 6: Compatibility checking
    print("=" * 70)
    print("Example 6: Strict Compatibility Checking")
    print("  Ensure backend can execute the circuit")
    print("-" * 70)

    print("\n  With strict compatibility (default):")
    try:
        strict_rec = selector.select_backend(qc, require_compatible=True)
        print(f"  ✓ Compatible backend: {strict_rec.backend.name}")
    except RuntimeError as e:
        print(f"  ✗ Error: {e}")
    print()

    print("=" * 70)
    print("Advanced examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
