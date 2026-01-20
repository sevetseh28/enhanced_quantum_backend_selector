"""Benchmark runner for Enhanced Quantum Backend Selector.

This script runs comprehensive benchmarks on the backend selector using real-world
quantum circuits. It collects metrics including transpilation time, circuit properties,
error rates, and backend selection quality.

Usage:
    python benchmarks/run_benchmarks.py [--output OUTPUT_DIR]
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from qiskit_ibm_runtime.fake_provider import FakeTorino

from benchmarks.circuits.benchmark_circuits import (
    create_2d_grid_ising,
    create_bernstein_vazirani_circuit,
    create_deep_linear_circuit,
    create_ghz_circuit,
    create_lucj_ansatz,
    create_mirror_circuit,
    create_qaoa_circuit,
    create_shallow_wide_circuit,
)
from benchmarks.mock_backends import get_all_mock_backends, get_backend_info
from enhanced_quantum_backend_selector import BackendSelector


def collect_circuit_metrics(circuit: Any) -> dict[str, Any]:
    """Collect metrics about a quantum circuit.

    Args:
        circuit: QuantumCircuit to analyze.

    Returns:
        Dictionary containing circuit metrics.
    """
    return {
        "num_qubits": circuit.num_qubits,
        "depth": circuit.depth(),
        "size": circuit.size(),
        "num_nonlocal_gates": circuit.num_nonlocal_gates(),
        "ops": dict(circuit.count_ops()),
    }


def run_single_benchmark(
    name: str, circuit: Any, backends: list[Any], num_runs: int = 3
) -> dict[str, Any]:
    """Run benchmark for a single circuit.

    Args:
        name: Name of the benchmark.
        circuit: QuantumCircuit to benchmark.
        backends: List of backends to evaluate.
        num_runs: Number of runs for averaging (default: 3).

    Returns:
        Dictionary containing benchmark results.
    """
    print(f"\n{'=' * 70}")
    print(f"Benchmark: {name}")
    print(f"{'=' * 70}")

    # Collect circuit metrics
    circuit_metrics = collect_circuit_metrics(circuit)
    print(
        f"Circuit: {circuit_metrics['num_qubits']} qubits, "
        f"depth {circuit_metrics['depth']}, "
        f"{circuit_metrics['size']} gates"
    )

    # Run backend selection
    start_time = time.time()
    selector = BackendSelector(backends)
    recommendations = selector.rank_backends(circuit, top_n=len(backends))
    selection_time = time.time() - start_time

    print(f"Selection time: {selection_time:.3f}s")
    print(f"\nAll {len(recommendations)} backends ranked:")

    # Build backend info map for processor types
    backend_info_map = {b.name: get_backend_info(b) for b in backends}

    results = []
    for i, rec in enumerate(recommendations, 1):
        error_pct = -rec.score_data.score * 100
        info = backend_info_map.get(rec.backend.name, {})
        proc_type = info.get("processor_type", "Unknown")
        print(
            f"  {i}. {rec.backend.name} ({proc_type}): {rec.score_data.score:.6f} ({error_pct:.3f}% error)"
        )
        results.append(
            {
                "rank": rec.rank,
                "backend": rec.backend.name,
                "processor_type": proc_type,
                "score": rec.score_data.score,
                "error_percent": error_pct,
                "compatible": rec.score_data.compatible,
            }
        )

    return {
        "name": name,
        "circuit_metrics": circuit_metrics,
        "selection_time_seconds": selection_time,
        "num_backends_evaluated": len(backends),
        "rankings": results,
        "timestamp": datetime.now().isoformat(),
    }


def run_all_benchmarks(output_dir: Path | None = None) -> dict[str, Any]:
    """Run all benchmark circuits.

    Args:
        output_dir: Directory to save results. If None, uses benchmarks/results.

    Returns:
        Dictionary containing all benchmark results.
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Enhanced Quantum Backend Selector - Benchmark Suite")
    print("=" * 70)

    # Create mock backends representing real IBM processors
    print("\nInitializing mock backends (representing real IBM processors)...")
    backends = get_all_mock_backends()
    print(f"  Created {len(backends)} mock backends:")
    for backend in backends:
        info = get_backend_info(backend)
        print(f"    • {info['name']}: {backend.num_qubits} qubits ({info['processor_type']})")

    # Define benchmark circuits - diverse set to showcase different backend trade-offs
    #
    # Expected winners based on circuit characteristics:
    # - 2D Grid Ising: Nighthawk (square lattice topology)
    # - Shallow Wide 130q: Heron R2/R3 only (>120 qubits excludes Nighthawk)
    # - Deep Linear: Best error rates (Heron R3 expected)
    # - QV-style: Best overall fidelity (Heron R3 expected)
    # - LUCJ Heavy-hex: Heron family (native heavy-hex topology)
    # - Mirror 5k: Tests accumulated gate errors (device stress test)
    # - GHZ/BV: Simple circuits, best calibrated qubits win
    #
    benchmarks = [
        # Small baseline circuits
        ("GHZ-10", create_ghz_circuit(10)),
        ("BernsteinVazirani-10", create_bernstein_vazirani_circuit(10)),
        # 2D Grid - favors square lattice (Nighthawk)
        ("Ising2D-5x5", create_2d_grid_ising(rows=5, cols=5, num_layers=3)),
        # Large qubit count - excludes Nighthawk (120q limit)
        ("ShallowWide-130q", create_shallow_wide_circuit(num_qubits=130)),
        ("GHZ-127", create_ghz_circuit(127)),  # Just above Nighthawk's 120q
        # Deep circuits - favors lowest error rates
        ("DeepLinear-20q-d30", create_deep_linear_circuit(num_qubits=20, depth=30)),
        # Mirror circuit - IBM's 1D Ising Trotter mirror (U†U=I, uses FakeTorino topology)
        (
            "Mirror-1D-50q",
            create_mirror_circuit(FakeTorino(), num_qubits=50, target_num_2q_gates=100),
        ),
        # Chemistry - favors heavy-hex topology
        ("LUCJ-Chemistry-52q", create_lucj_ansatz(52, n_reps=1, topology="heavy_hex")),
        # Optimization
        ("QAOA-Ring-12q", create_qaoa_circuit(12, num_layers=2)),
    ]

    # Run benchmarks
    all_results = []
    for name, circuit in benchmarks:
        result = run_single_benchmark(name, circuit, backends)
        all_results.append(result)

    # Compile summary
    summary = {
        "benchmark_suite": "Enhanced Quantum Backend Selector",
        "timestamp": datetime.now().isoformat(),
        "num_benchmarks": len(all_results),
        "num_backends": len(backends),
        "results": all_results,
    }

    # Save results
    output_file = output_dir / f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'=' * 70}")
    print("Benchmark Summary")
    print(f"{'=' * 70}")
    print(f"Total benchmarks: {len(all_results)}")
    print(f"Results saved to: {output_file}")

    return summary


def main() -> None:
    """Main entry point for benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Run benchmarks for Enhanced Quantum Backend Selector"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory for results (default: benchmarks/results)",
    )
    args = parser.parse_args()

    run_all_benchmarks(args.output)

    print("\n" + "=" * 70)
    print("Benchmarking completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
