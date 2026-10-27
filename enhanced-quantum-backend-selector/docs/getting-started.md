# Getting Started

This guide covers installation and basic usage of the Enhanced Quantum Backend Selector.

## Installation

### Requirements

- Python 3.10 or higher
- Qiskit 2.2.3 or higher

### Install from PyPI

```bash
pip install enhanced-quantum-backend-selector
```

### Install with Poetry

```bash
poetry add enhanced-quantum-backend-selector
```

### Install from GitHub

```bash
pip install git+https://github.com/sevetseh28/enhanced_quantum_backend_selector.git#subdirectory=enhanced-quantum-backend-selector
```

### Install from Source (Development)

```bash
git clone https://github.com/sevetseh28/enhanced_quantum_backend_selector.git
cd enhanced-quantum-backend-selector/enhanced-quantum-backend-selector
poetry install
```

## Basic Usage

### 1. Get Available Backends

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backends = service.backends()
```

!!! tip "Using Fake Backends for Testing"
    **Generic backends (Qiskit):**
    ```python
    from qiskit.providers.fake_provider import GenericBackendV2

    backends = [
        GenericBackendV2(num_qubits=5),
        GenericBackendV2(num_qubits=27),
    ]
    ```

    **Fake IBM backends (qiskit-ibm-runtime):**
    ```python
    from qiskit_ibm_runtime.fake_provider import FakeManilaV2, FakeSherbrooke

    backends = [FakeManilaV2(), FakeSherbrooke()]
    ```

### 2. Create a Circuit

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()
```

### 3. Select the Best Backend

```python
from enhanced_quantum_backend_selector import BackendSelector

selector = BackendSelector(backends)
rec = selector.select_backend(qc)

print(f"Best backend: {rec.backend.name}")
print(f"Score: {rec.score_data.score:.3f}")
print(f"Expected error: {1 - rec.score_data.score:.2%}")
```

### 4. Understanding Scores

- **Score** is the estimated success probability (ESP): the chance the circuit runs without error, between 0 and 1. It is the product of `(1 - error)` over every gate, every used qubit's readout, and the time each qubit spends idle
- **Higher scores are better**: `0.99` (1% error) is better than `0.95` (5% error)

The score is calculated by:

1. Transpiling your circuit to the backend (optimization level 2)
2. Multiplying `(1 - error)` for every gate, readout and idle period in the transpiled circuit
3. Averaging over multiple transpilation runs (default: 3)

## Complete Example

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

print(f"✓ Selected: {rec.backend.name}")
print(f"  Score: {rec.score_data.score:.3f}")
print(f"  Expected error: {1 - rec.score_data.score:.2%}")
```

## Troubleshooting

### ModuleNotFoundError: No module named 'qiskit_ibm_runtime'

```bash
pip install qiskit-ibm-runtime
```

### Authentication Error

```python
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    channel="ibm_quantum",
    token="YOUR_API_TOKEN",
    overwrite=True
)
```

### No Compatible Backends Found

```python
# Get all rankings to see what's available
rankings = selector.rank_backends(qc)
for rec in rankings:
    print(f"{rec.backend.name}: {rec.score_data.score:.3f}")
```

## Next Steps

- [User Guide](user-guide.md) - Advanced features and configuration
- [Examples](examples.md) - Real-world usage patterns
- [API Reference](api-reference.md) - Complete API documentation
