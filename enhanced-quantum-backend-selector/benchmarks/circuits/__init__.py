"""Real-world quantum circuit implementations for benchmarking.

This module provides various circuit families including:
- GHZ: Greenberger-Horne-Zeilinger states
- Bernstein-Vazirani: Hidden string problem
- Mirror circuits: Device benchmarking (Loschmidt echo)
- LUCJ: Chemistry applications
- QAOA: Optimization problems
- 2D Ising: Grid topology simulation
"""

from benchmarks.circuits.benchmark_circuits import (
    create_2d_grid_ising,
    create_bernstein_vazirani_circuit,
    create_deep_linear_circuit,
    create_ghz_circuit,
    create_lucj_ansatz,
    create_mirror_5k_circuit,
    create_mirror_circuit,
    create_qaoa_circuit,
    create_shallow_wide_circuit,
)

__all__ = [
    "create_ghz_circuit",
    "create_bernstein_vazirani_circuit",
    "create_mirror_circuit",
    "create_mirror_5k_circuit",  # backward compatibility alias
    "create_lucj_ansatz",
    "create_qaoa_circuit",
    "create_2d_grid_ising",
    "create_shallow_wide_circuit",
    "create_deep_linear_circuit",
]
