# Benchmarking

This guide describes the benchmarking framework for evaluating the backend selector.

## Overview

The benchmarking suite evaluates performance using real-world quantum circuits from various application domains.

## Benchmark Circuits

### GHZ States

Test multi-qubit entanglement and connectivity.

```python
# H(q0) → CX(q0,q1) → CX(q1,q2) → ...
```

### Bernstein-Vazirani

Test parallel operations and phase kickback.

### Mirror Circuits

Test device fidelity through circuit inversion. The circuit and its inverse should return to |0⟩.

### LUCJ Ansatz

Chemistry ansatz for quantum chemistry applications. Reference: [arXiv:2511.22476](https://arxiv.org/pdf/2511.22476)

### QAOA

Quantum Approximate Optimization Algorithm for combinatorial optimization.

## Mock Backends

The benchmarks use mock backends simulating real IBM processors:

| Backend | Qubits | Topology | Generation |
|---------|--------|----------|------------|
| IBM Heron R1 | 133 | Heavy-hex | 2023 |
| IBM Heron R2 | 156 | Heavy-hex | 2024 |
| IBM Nighthawk | 120 | Square lattice | 2025 |

## Running Benchmarks

```bash
cd enhanced-quantum-backend-selector
poetry run python benchmarks/run_benchmarks.py
```

Results are saved to `benchmarks/results/` with timestamps.

### Custom Output Directory

```bash
poetry run python benchmarks/run_benchmarks.py --output /path/to/results
```

## Result Format

```json
{
  "benchmark_suite": "Enhanced Quantum Backend Selector",
  "timestamp": "2026-01-07T01:05:48.123456",
  "results": [
    {
      "name": "GHZ-5",
      "circuit_metrics": {
        "num_qubits": 5,
        "depth": 6,
        "num_nonlocal_gates": 4
      },
      "selection_time_seconds": 0.543,
      "rankings": [
        {
          "rank": 1,
          "backend": "ibm_nighthawk",
          "score": 0.992534,
          "error_percent": 0.747
        }
      ]
    }
  ]
}
```

## Metrics Collected

**Circuit Metrics:**

- `num_qubits`: Number of qubits
- `depth`: Circuit depth
- `num_nonlocal_gates`: Two-qubit gate count

**Performance Metrics:**

- `selection_time_seconds`: Time to select backend
- `score`: Estimated success probability, 0 to 1
- `error_percent`: Expected error percentage

## Adding New Benchmarks

1. Add circuit function to `benchmarks/circuits/benchmark_circuits.py`:

```python
def create_new_circuit(num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits, name="NewCircuit")
    # Add gates
    qc.measure_all()
    return qc
```

2. Export in `benchmarks/circuits/__init__.py`
3. Add to suite in `benchmarks/run_benchmarks.py`

## Validation

```bash
poetry run pytest tests/test_benchmarks.py -v
```

## References

- [Qiskit Benchpress](https://github.com/Qiskit/benchpress)
- [qiskit-device-benchmarking](https://github.com/qiskit-community/qiskit-device-benchmarking)
- [LUCJ Ansatz Paper](https://arxiv.org/pdf/2511.22476)
