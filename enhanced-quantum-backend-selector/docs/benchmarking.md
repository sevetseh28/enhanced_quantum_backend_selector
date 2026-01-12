# Benchmarking Guide

This guide describes the benchmarking framework for the Enhanced Quantum Backend Selector, including methodology, circuit selection, and metrics.

## Overview

The benchmarking suite evaluates the performance, accuracy, and robustness of the backend selector using real-world quantum circuits. It implements circuits from various application domains and measures key performance indicators.

## Benchmark Circuits

### 1. GHZ (Greenberger-Horne-Zeilinger) States

**Purpose**: Test multi-qubit entanglement and long-range connectivity.

**Implementation**: `create_ghz_circuit(num_qubits)`

**Circuit Structure**:
```
H(q0) → CX(q0,q1) → CX(q1,q2) → ... → CX(qn-2,qn-1)
```

**Key Metrics**:
- Multi-qubit entanglement fidelity
- Long-range qubit connectivity
- CNOT gate error rates

**Reference**: Standard quantum benchmarking circuit

---

### 2. Bernstein-Vazirani Algorithm

**Purpose**: Test parallel operations and phase kickback mechanisms.

**Implementation**: `create_bernstein_vazirani_circuit(num_qubits, hidden_string="111...")`

**Circuit Structure**:
- Initialization with ancilla in |-> state
- Parallel Hadamard gates
- Oracle (controlled-X based on hidden string)
- Final Hadamard transform

**Key Metrics**:
- Parallel gate execution
- Phase coherence
- Hadamard transform efficiency

**Reference**: [Qiskit Benchpress](https://github.com/Qiskit/benchpress)

---

### 3. Mirror_5k Circuit

**Purpose**: Device benchmarking through circuit inversion.

**Implementation**: `create_mirror_5k_circuit(num_qubits=5, depth=100)`

**Circuit Structure**:
- Random circuit of specified depth
- Inverse of the random circuit
- Should return to |0⟩ state (ideal)

**Key Metrics**:
- Gate fidelity across many operations
- Coherence time under extended operations
- Deviation from ideal return state

**Reference**: [qiskit-device-benchmarking Mirror Circuits](https://github.com/qiskit-community/qiskit-device-benchmarking/blob/main/qiskit_device_benchmarking/mirror_test/mirror_circuits.py)

---

### 4. LUCJ Ansatz (Chemistry)

**Purpose**: Evaluate performance on quantum chemistry applications.

**Implementation**: `create_lucj_ansatz(num_qubits, n_reps=1)`

**Circuit Structure**:
- Hartree-Fock initialization
- Layered unitary cluster operators
- Jastrow-type correlations
- Parameterized rotations

**Key Metrics**:
- Variational algorithm support
- Parameterized gate handling
- Chemistry-specific gate sequences

**Reference**: [arXiv:2511.22476](https://arxiv.org/pdf/2511.22476) - LUCJ Ansatz paper

---

### 5. QAOA (Optimization)

**Purpose**: Test optimization algorithm performance.

**Implementation**: `create_qaoa_circuit(num_qubits, num_layers=1)`

**Circuit Structure**:
- Initial Hadamard layer
- Alternating cost and mixer unitaries
- Problem: MaxCut on ring graph

**Key Metrics**:
- Variational optimization support
- Mixer and cost operator implementation
- Parameter optimization overhead

**Reference**: [Qiskit Benchpress](https://github.com/Qiskit/benchpress)

---

## Methodology

### Mock Backends Representing Real IBM Processors

To ensure realistic benchmarking, we use mock backends that simulate real IBM Quantum processors with accurate specifications:

#### **IBM Quantum Heron R1** (ibm_heron_r1)
- 133 qubits with heavy-hex lattice topology
- ~1% two-qubit gate error rates
- Supports up to 1,800 two-qubit gates per circuit
- Generation: 2023
- Strengths: Reliable baseline performance

#### **IBM Quantum Heron R2** (ibm_heron_r2)
- 156 qubits with heavy-hex lattice topology
- Sub-1% two-qubit gate error rates
- Improved TLS (Two-Level System) mitigation
- Supports up to 5,000 two-qubit gates per circuit
- Generation: 2024
- Strengths: Deep circuits, high fidelity, complex entanglement

#### **IBM Quantum Nighthawk** (ibm_nighthawk)
- 120 qubits with square lattice topology
- Each qubit connected to 4 neighbors (218 tunable couplers)
- Sub-1% two-qubit gate error rates
- Superior T1 coherence time: ~350 microseconds
- 30% more circuit complexity than Heron
- Generation: 2025
- Strengths: Better connectivity, excellent for optimization and variational algorithms

These mock backends allow testing whether the selector can:
1. Distinguish between processor generations (Heron R1 vs R2)
2. Identify topology advantages (heavy-hex vs square lattice)
3. Recognize when connectivity matters (Nighthawk's 4-neighbor topology)
4. Select based on real-world processor characteristics

### Backend Selection Process

1. **Circuit Transpilation**: Each circuit is transpiled to each backend's native gate set
2. **Error Calculation**: Sum of gate error rates for transpiled operations
3. **Multiple Runs**: Average over 3 transpilation runs for stability
4. **Ranking**: Backends ranked by score (negative total error)

### Metrics Collected

For each benchmark run, we collect:

#### Circuit Metrics
- `num_qubits`: Number of qubits in circuit
- `depth`: Circuit depth (critical path length)
- `size`: Total number of gates
- `num_nonlocal_gates`: Number of two-qubit gates
- `ops`: Gate operation counts by type

#### Performance Metrics
- `selection_time_seconds`: Time to select best backend
- `score`: Backend compatibility score (negative error)
- `error_percent`: Expected error percentage
- `compatible`: Whether backend can execute circuit

#### Ranking Metrics
- `rank`: Backend position in ranking
- `backend`: Backend name
- `score`: Compatibility score
- `error_percent`: Error rate as percentage

### Running Benchmarks

#### Full Benchmark Suite

Run all benchmarks with:

```bash
cd enhanced-quantum-backend-selector
poetry run python benchmarks/run_benchmarks.py
```

Results are saved to `benchmarks/results/` with timestamp.

#### Custom Output Directory

```bash
poetry run python benchmarks/run_benchmarks.py --output /path/to/results
```

#### Example Script

Run the example benchmarks:

```bash
poetry run python examples/run_benchmarks.py
```

### Result Format

Results are saved as JSON with the following structure:

```json
{
  "benchmark_suite": "Enhanced Quantum Backend Selector",
  "timestamp": "2026-01-07T01:05:48.123456",
  "num_benchmarks": 5,
  "num_backends": 3,
  "results": [
    {
      "name": "GHZ-5",
      "circuit_metrics": {
        "num_qubits": 5,
        "depth": 6,
        "size": 10,
        "num_nonlocal_gates": 4,
        "ops": {"h": 1, "cx": 4, "measure": 5}
      },
      "selection_time_seconds": 0.543,
      "rankings": [
        {
          "rank": 1,
          "backend": "ibm_nighthawk",
          "score": -0.007466,
          "error_percent": 0.747,
          "compatible": true
        }
      ]
    }
  ]
}
```

## Benchmarking Strategies

### 1. Device Benchmarking (Mirror Circuits)

Mirror circuits test device fidelity by executing a circuit and its inverse. The final state should match the initial state, with deviations indicating accumulated errors.

**Key Insights**:
- Tests cumulative gate errors
- Measures decoherence effects
- Validates transpilation quality

**Reference**: [qiskit-device-benchmarking](https://github.com/qiskit-community/qiskit-device-benchmarking)

### 2. Transpilation Performance

The benchmark suite measures transpilation time as a key metric. Faster transpilation enables:
- Rapid backend evaluation
- Real-time backend switching
- Efficient workflow integration

**Reference**: [Qiskit Benchpress](https://github.com/Qiskit/benchpress)

### 3. Application-Specific Benchmarks

Different circuits test suitability for specific applications:
- **Chemistry**: LUCJ ansatz with parameterized gates
- **Optimization**: QAOA with alternating unitaries
- **Algorithm Testing**: BV for parallel operations

## Extensibility

### Adding New Benchmark Circuits

1. Add circuit function to `benchmarks/circuits/benchmark_circuits.py`:

```python
def create_new_circuit(num_qubits: int) -> QuantumCircuit:
    """Create new benchmark circuit."""
    qc = QuantumCircuit(num_qubits, name="NewCircuit")
    # Add gates
    qc.measure_all()
    return qc
```

2. Export in `benchmarks/circuits/__init__.py`
3. Add to benchmark suite in `benchmarks/run_benchmarks.py`
4. Add tests in `tests/test_benchmarks.py`

### Custom Metrics

Extend `collect_circuit_metrics()` in `benchmarks/run_benchmarks.py` to add custom metrics:

```python
def collect_circuit_metrics(circuit: Any) -> dict[str, Any]:
    """Collect metrics about a quantum circuit."""
    return {
        "num_qubits": circuit.num_qubits,
        "depth": circuit.depth(),
        # Add custom metrics here
        "custom_metric": calculate_custom_metric(circuit),
    }
```

## CI/CD Integration

Benchmarks run automatically in CI/CD via the `benchmarks.yml` workflow (see CI/CD section below).

### Manual Trigger

Benchmarks can be triggered manually through GitHub Actions:
1. Go to Actions tab
2. Select "Benchmarks" workflow
3. Click "Run workflow"

### Scheduled Runs

Benchmarks run on a schedule to track performance over time:
- Weekly on Sunday at 00:00 UTC
- Results archived as artifacts

## References

### Primary Sources

1. **Qiskit Benchpress**: Comprehensive quantum circuit benchmarking
   - https://github.com/Qiskit/benchpress
   - [Circuit Examples](https://github.com/Qiskit/benchpress/blob/a9744133a5fb227201caac014fba65c41ae9df3d/benchpress/qiskit_gym/circuits/circuits.py#L59-L75)

2. **qiskit-device-benchmarking**: Device characterization and benchmarking
   - https://github.com/qiskit-community/qiskit-device-benchmarking
   - [Mirror Circuits](https://github.com/qiskit-community/qiskit-device-benchmarking/blob/main/qiskit_device_benchmarking/mirror_test/mirror_circuits.py)

3. **LUCJ Ansatz**: Advanced chemistry ansatz
   - [arXiv:2511.22476](https://arxiv.org/pdf/2511.22476)

4. **Benchmarking Publication**: Nature paper on quantum benchmarking
   - https://www.nature.com/articles/s43588-025-00792-y

### Additional Resources

- Qiskit documentation: https://docs.quantum.ibm.com/
- Quantum algorithm zoo: https://quantumalgorithmzoo.org/
- Qiskit textbook: https://qiskit.org/textbook/

## Validation and Reproducibility

### Reproducibility

All benchmarks use fixed random seeds for reproducibility:
- Mirror circuits: `seed=42`
- Test backends: `seed=200, 201, 202`

### Validation

Tests ensure:
- All circuits can be created successfully
- Circuits have expected properties
- Measurements are included
- Gate counts are reasonable

Run validation tests:

```bash
poetry run pytest tests/test_benchmarks.py -v
```

## Performance Expectations

Typical benchmark run times on standard hardware:
- GHZ circuits: ~0.5s
- Bernstein-Vazirani: ~0.1s
- Mirror_5k: ~0.4s (due to high gate count)
- LUCJ ansatz: ~0.1s
- QAOA: ~0.1s

Total suite runtime: ~1-2 seconds

## Contributing

To contribute new benchmarks:

1. Follow the circuit implementation pattern in `benchmark_circuits.py`
2. Add comprehensive docstrings with references
3. Include tests for validation
4. Update this documentation
5. Submit PR with example results

See the [Contributing Guide](contributing.md) for details.
