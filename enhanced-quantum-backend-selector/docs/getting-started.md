# Getting Started

This guide will help you install and start using the Enhanced Quantum Backend Selector.

## Installation

### Requirements

- Python 3.12 or higher
- Qiskit 2.2.3 or higher (with BackendV2 support)

### Install from PyPI

The easiest way to install is via pip:

```bash
pip install enhanced-quantum-backend-selector
```

### Install with Poetry

If you use Poetry for dependency management:

```bash
poetry add enhanced-quantum-backend-selector
```

### Install from Source

For development or the latest unreleased features:

```bash
git clone https://github.com/sevetseh28/enhanced_quantum_backend_selector.git
cd enhanced-quantum-backend-selector/enhanced-quantum-backend-selector
poetry install
```

## Verify Installation

Test that the library is installed correctly:

```python
from enhanced_quantum_backend_selector import BackendSelector
print("Installation successful!")
```

## First Steps

### 1. Get Available Backends

Connect to a quantum provider and retrieve available backends:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

# Initialize service (requires IBM Quantum account)
service = QiskitRuntimeService()

# Get all available backends
backends = service.backends()
print(f"Found {len(backends)} backends")
```

!!! tip "Using Simulators for Testing"
    For testing without an IBM Quantum account, use Qiskit's fake backends:
    
    ```python
    from qiskit.providers.fake_provider import GenericBackendV2
    
    backends = [
        GenericBackendV2(num_qubits=5),
        GenericBackendV2(num_qubits=7),
        GenericBackendV2(num_qubits=27),
    ]
    ```

### 2. Create a Quantum Circuit

Define the circuit you want to execute:

```python
from qiskit import QuantumCircuit

# Create a simple GHZ state
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()
```

### 3. Select the Best Backend

Use the BackendSelector to find the optimal backend:

```python
from enhanced_quantum_backend_selector import BackendSelector

# Initialize selector with available backends
selector = BackendSelector(backends)

# Get the best backend for your circuit
recommendation = selector.select_backend(qc)

# Use the recommended backend
print(f"Best backend: {recommendation.backend.name}")
print(f"Score: {recommendation.score_data.score:.3f}")
```

### 4. Understanding the Results

The recommendation includes detailed information:

```python
# Overall metrics
print(f"Rank: #{recommendation.rank}")
print(f"Score: {recommendation.score_data.score:.3f}")  # Negative error sum
print(f"Compatible: {recommendation.score_data.compatible}")

# Human-readable explanation
for reason in recommendation.score_data.reasons:
    print(f"  • {reason}")

# Backend specifications
print("\nBackend Details:")
print(f"  Num Qubits:     {recommendation.metrics.num_qubits}")
print(f"  Connectivity:   {recommendation.metrics.num_edges} edges")
if recommendation.metrics.avg_t1:
    print(f"  Avg T1 Time:    {recommendation.metrics.avg_t1:.2e} seconds")
```

**Understanding Scores:**

- Score is the **negative sum of all errors**: `score = -total_error`
- **Higher scores are better** (less negative = lower error)
- Example: `-0.01` (1% error) is better than `-0.05` (5% error)
- Score is calculated by:
  1. Transpiling your circuit to the backend (optimization level 2)
  2. Summing all error rates for the qubits used in the transpiled circuit
  3. Averaging over 3 independent transpilation runs

### 5. Execute Your Circuit

Once you have the recommendation, execute your circuit:

```python
from qiskit_ibm_runtime import Sampler

# Use the recommended backend
backend = recommendation.backend

# Create a sampler and run the circuit
sampler = Sampler(backend=backend)
job = sampler.run(qc, shots=1024)
result = job.result()

print(f"Job completed on {backend.name}")
```

## Complete Example

Here's a complete working example:

```python
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from enhanced_quantum_backend_selector import BackendSelector

# Setup
backends = [
    GenericBackendV2(num_qubits=5),
    GenericBackendV2(num_qubits=7),
    GenericBackendV2(num_qubits=27),
]

# Create circuit
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

# Select backend
selector = BackendSelector(backends)
recommendation = selector.select_backend(qc)

# Display results
print(f"✓ Selected: {recommendation.backend.name}")
print(f"  Score: {recommendation.score_data.score:.3f}")
print(f"  Reasons: {', '.join(recommendation.score_data.reasons)}")
```

## Next Steps

Now that you have the basics working, explore:

- [User Guide](user-guide.md) - Learn about custom weights and advanced features
- [Examples](examples.md) - See real-world usage patterns
- [API Reference](api-reference.md) - Complete API documentation

## Common Issues

### ModuleNotFoundError: No module named 'qiskit_ibm_runtime'

Install the IBM Quantum Runtime package:

```bash
pip install qiskit-ibm-runtime
```

### Authentication Error

Set up your IBM Quantum credentials:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

# Save credentials (first time only)
QiskitRuntimeService.save_account(
    channel="ibm_quantum",
    token="YOUR_API_TOKEN",
    overwrite=True
)
```

Get your API token from [IBM Quantum](https://quantum.ibm.com/).

### No Compatible Backends Found

If you get an error about no compatible backends:

```python
# Option 1: Disable strict compatibility checking
recommendation = selector.select_backend(qc, require_compatible=False)

# Option 2: Lower the minimum score threshold
recommendation = selector.select_backend(qc, min_score=0.1)

# Option 3: Get all rankings to see what's available
rankings = selector.rank_backends(qc)
for rec in rankings:
    print(f"{rec.backend.name}: {rec.score_data.score:.3f}")
```
