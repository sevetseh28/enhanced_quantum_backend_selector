# Examples

Practical examples of using the Enhanced Quantum Backend Selector.

## Running Examples

Examples are in the `examples/` directory:

```bash
cd enhanced-quantum-backend-selector
poetry run python examples/basic_usage.py
poetry run python examples/advanced_usage.py
```

## Basic Usage

```python
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from enhanced_quantum_backend_selector import BackendSelector

# Setup backends
backends = [
    GenericBackendV2(num_qubits=5, seed=42),
    GenericBackendV2(num_qubits=7, seed=43),
    GenericBackendV2(num_qubits=27, seed=44),
]

# Create circuit
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

# Select backend
selector = BackendSelector(backends)
rec = selector.select_backend(qc)

print(f"Recommended: {rec.backend.name}")
print(f"Score: {rec.score_data.score:.3f}")
print(f"Rank: #{rec.rank}")
```

## Compare Multiple Backends

```python
# Get top 3 backends
top_3 = selector.rank_backends(qc, top_n=3)

for rec in top_3:
    error_pct = -rec.score_data.score * 100
    print(f"{rec.rank}. {rec.backend.name}")
    print(f"   Score: {rec.score_data.score:.3f}")
    print(f"   Expected error: {error_pct:.2f}%")
```

## Chemistry Circuits

VQE and chemistry circuits benefit from fractional gates:

```python
from qiskit.circuit.library import EfficientSU2

# Create chemistry ansatz
ansatz = EfficientSU2(num_qubits=4, reps=2)
ansatz.measure_all()

# Select best backend
rec = selector.select_backend(ansatz)
print(f"Best backend: {rec.backend.name}")
print(f"Expected error: {-rec.score_data.score:.2%}")
```

To compare fractional vs standard gates:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backends = [
    service.backend('ibm_torino'),
    service.backend('ibm_torino', use_fractional_gates=True),
]
```

## VQE Circuit

```python
def create_vqe_circuit(num_qubits=4):
    qc = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        qc.ry(0.1 * i, i)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc

qc = create_vqe_circuit(4)
rec = selector.select_backend(qc)

print(f"Best VQE backend: {rec.backend.name}")
print(f"Expected error: {-rec.score_data.score:.4f}")
```

## QAOA Circuit

```python
def create_qaoa_circuit(num_qubits=6):
    qc = QuantumCircuit(num_qubits)

    # Initial superposition
    for i in range(num_qubits):
        qc.h(i)

    # Problem Hamiltonian
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)]
    for i, j in edges:
        qc.cx(i, j)
        qc.rz(0.5, j)
        qc.cx(i, j)

    qc.measure_all()
    return qc

qc = create_qaoa_circuit(6)
rec = selector.select_backend(qc)
print(f"Best QAOA backend: {rec.backend.name}")
```

## Production Workflow

```python
def production_backend_selection(circuit, backends):
    """Production-ready backend selection with error handling."""
    selector = BackendSelector(backends)

    try:
        rec = selector.select_backend(circuit, require_compatible=True)

        error_pct = -rec.score_data.score * 100
        if error_pct < 10:
            return rec.backend, "optimal"
        else:
            return rec.backend, "acceptable"

    except RuntimeError as e:
        # No backend can run this circuit; each backend's reasons say why
        print(f"Warning: {e}")
        for rec in selector.rank_backends(circuit):
            print(f"  {rec.backend.name}: {rec.score_data.reasons[0]}")
        return None, "unavailable"

backend, quality = production_backend_selection(qc, backends)
print(f"Selected: {backend.name} (quality: {quality})")
```

## Batch Processing

```python
def batch_backend_selection(circuits, backends):
    """Select backends for multiple circuits."""
    selector = BackendSelector(backends)

    results = {}
    for i, circuit in enumerate(circuits):
        rec = selector.select_backend(circuit)
        error_pct = -rec.score_data.score * 100
        results[f"circuit_{i}"] = {
            "backend": rec.backend.name,
            "score": rec.score_data.score,
            "error_pct": error_pct,
        }
        print(f"Circuit {i}: {rec.backend.name} ({error_pct:.2f}% error)")

    return results
```

## Backend Comparison Table

```python
def compare_backends(circuit, backends, top_n=5):
    """Compare top backends for a circuit."""
    selector = BackendSelector(backends)
    recommendations = selector.rank_backends(circuit, top_n=top_n)

    print(f"{'Rank':<6} {'Backend':<25} {'Score':>10} {'Error %':>10}")
    print("-" * 55)

    for rec in recommendations:
        error_pct = -rec.score_data.score * 100
        print(f"#{rec.rank:<5} {rec.backend.name:<25} "
              f"{rec.score_data.score:>10.4f} {error_pct:>9.2f}%")

compare_backends(qc, backends)
```

## Next Steps

- [User Guide](user-guide.md) - Learn about all features
- [API Reference](api-reference.md) - Complete API documentation
- [Benchmarking](benchmarking.md) - Benchmark circuits and methodology
