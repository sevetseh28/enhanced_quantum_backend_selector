"""Advanced usage example for Enhanced Quantum Backend Selector.

This example demonstrates:
1. Custom scoring weights for different optimization goals
2. Comparing multiple scoring strategies
3. Handling edge cases (incompatible backends, minimum scores)
4. Understanding the impact of different weight configurations
"""

from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2

from enhanced_quantum_backend_selector import (
    BackendRecommendation,
    BackendSelector,
    ScoringWeights,
)


def print_recommendation(rec: BackendRecommendation, strategy: str) -> None:
    """Print formatted recommendation details."""
    print(f"\n  Strategy: {strategy}")
    print(f"  Backend:  {rec.backend.name}")
    print(f"  Score:    {rec.score_data.score:.3f}")
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

    # Example 1: Quality-First Strategy
    print("=" * 70)
    print("Example 1: Quality-First Strategy")
    print("  Prioritize gate fidelity and coherence over queue time")
    print("-" * 70)

    quality_weights = ScoringWeights(
        gate_fidelity_weight=2.0,   # Very high priority
        connectivity_weight=1.5,     # High priority
        coherence_weight=1.5,        # High priority
        queue_weight=0.2,            # Low priority - we don't care about waiting
    )

    quality_rec = selector.select_backend(qc, weights=quality_weights)
    print_recommendation(quality_rec, "Quality-First")
    print()

    # Example 2: Speed-First Strategy
    print("=" * 70)
    print("Example 2: Speed-First Strategy")
    print("  Prioritize queue time - get results quickly")
    print("-" * 70)

    speed_weights = ScoringWeights(
        gate_fidelity_weight=0.5,    # Lower priority
        connectivity_weight=0.8,     # Moderate priority
        coherence_weight=0.5,        # Lower priority
        queue_weight=3.0,            # Very high priority - minimize wait
    )

    speed_rec = selector.select_backend(qc, weights=speed_weights)
    print_recommendation(speed_rec, "Speed-First")
    print()

    # Example 3: Balanced Strategy (default)
    print("=" * 70)
    print("Example 3: Balanced Strategy")
    print("  Default weights - balanced approach")
    print("-" * 70)

    # Using default weights
    balanced_rec = selector.select_backend(qc)
    print_recommendation(balanced_rec, "Balanced (Default)")
    print()

    # Example 4: Connectivity-First Strategy
    print("=" * 70)
    print("Example 4: Connectivity-First Strategy")
    print("  For circuits with complex coupling requirements")
    print("-" * 70)

    connectivity_weights = ScoringWeights(
        gate_fidelity_weight=1.0,
        connectivity_weight=3.0,     # Very high - need good topology match
        coherence_weight=1.0,
        queue_weight=0.5,
    )

    connectivity_rec = selector.select_backend(qc, weights=connectivity_weights)
    print_recommendation(connectivity_rec, "Connectivity-First")
    print()

    # Example 5: Compare all strategies side-by-side
    print("=" * 70)
    print("Example 5: Strategy Comparison Summary")
    print("-" * 70)

    strategies = [
        ("Quality-First", quality_rec),
        ("Speed-First", speed_rec),
        ("Balanced", balanced_rec),
        ("Connectivity-First", connectivity_rec),
    ]

    print("\n  Backend Selection Summary:")
    print("  " + "-" * 66)
    print(f"  {'Strategy':<20} {'Backend':<25} {'Score':>8} {'Qubits':>8}")
    print("  " + "-" * 66)

    for strategy, rec in strategies:
        print(f"  {strategy:<20} {rec.backend.name:<25} "
              f"{rec.score_data.score:>8.3f} {rec.metrics.num_qubits:>8}")
    print()

    # Example 6: Minimum score filtering
    print("=" * 70)
    print("Example 6: Minimum Score Filtering")
    print("  Require backends to meet quality threshold")
    print("-" * 70)

    min_score = -0.1  # Negative score: lower error = higher (less negative) score
    print(f"\n  Minimum acceptable score: {min_score}")
    print("  (Note: Scores are negative error sums; -0.01 is better than -0.1)")

    try:
        filtered_rec = selector.select_backend(qc, min_score=min_score)
        print(f"  ✓ Found backend: {filtered_rec.backend.name} "
              f"(score: {filtered_rec.score_data.score:.3f})")
    except ValueError as e:
        print(f"  ✗ No backends met minimum score: {e}")
    print()

    # Example 7: Compatibility checking
    print("=" * 70)
    print("Example 7: Strict Compatibility Checking")
    print("  Ensure backend can execute the circuit")
    print("-" * 70)

    print("\n  With strict compatibility (default):")
    try:
        strict_rec = selector.select_backend(qc, require_compatible=True)
        print(f"  ✓ Compatible backend: {strict_rec.backend.name}")
    except ValueError as e:
        print(f"  ✗ Error: {e}")

    print("\n  Without strict compatibility:")
    lenient_rec = selector.select_backend(qc, require_compatible=False)
    print(f"  ✓ Selected: {lenient_rec.backend.name}")
    print()

    # Example 8: Full ranking with custom top_n
    print("=" * 70)
    print("Example 8: Full Rankings")
    print("  Get all backends ranked for comparison")
    print("-" * 70)

    all_rankings = selector.rank_backends(qc, top_n=None)  # Get all

    print(f"\n  Complete Backend Rankings ({len(all_rankings)} backends):")
    print("  " + "-" * 66)
    print(f"  {'Rank':>4} {'Backend':<25} {'Score':>8} {'Qubits':>8} {'Status':<15}")
    print("  " + "-" * 66)

    for rec in all_rankings:
        status = "✓ Compatible" if rec.score_data.compatible else "✗ Incompatible"
        print(
            f"  {rec.rank:>4} {rec.backend.name:<25} "
            f"{rec.score_data.score:>8.3f} {rec.metrics.num_qubits:>8} {status:<15}"
        )
    print()

    print("=" * 70)
    print("Advanced examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
