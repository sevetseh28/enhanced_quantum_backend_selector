# Examples

This section provides practical examples of using the Enhanced Quantum Backend Selector in various scenarios.

## Running the Examples

All examples are available in the `examples/` directory of the repository:

```bash
# Clone the repository
git clone https://github.com/sevetseh28/enhanced_quantum_backend_selector.git
cd enhanced-quantum-backend-selector/enhanced-quantum-backend-selector

# Install dependencies
poetry install

# Run an example
poetry run python examples/basic_usage.py
poetry run python examples/advanced_usage.py
```

## Validate All Examples

Run the validation script to ensure all examples work:

```bash
poetry run python examples/validate_examples.py
```

## Basic Usage Example

[View full source code →](https://github.com/sevetseh28/enhanced_quantum_backend_selector/blob/main/enhanced-quantum-backend-selector/examples/basic_usage.py)

This example demonstrates the fundamental workflow:

```python
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from enhanced_quantum_backend_selector import BackendSelector

# Get available backends
backends = [
    GenericBackendV2(num_qubits=5, seed=42),
    GenericBackendV2(num_qubits=7, seed=43),
    GenericBackendV2(num_qubits=27, seed=44),
]

# Create a quantum circuit (GHZ state)
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

# Initialize selector and select best backend
selector = BackendSelector(backends)
recommendation = selector.select_backend(qc)

# View results
print(f"Recommended: {recommendation.backend.name}")
print(f"Score: {recommendation.score_data.score:.3f}")
print(f"Rank: #{recommendation.rank}")
```

**Key Concepts:**
- Creating a `BackendSelector` instance
- Using `select_backend()` for simple selection
- Understanding the `BackendRecommendation` object
- Accessing score breakdown and metrics

## Advanced Usage Example

[View full source code →](https://github.com/sevetseh28/enhanced_quantum_backend_selector/blob/main/enhanced-quantum-backend-selector/examples/advanced_usage.py)

This example shows advanced features:

```python
from enhanced_quantum_backend_selector import BackendSelector

# Create more complex circuit
qc = QuantumCircuit(5)
qc.h(0)
for i in range(4):
    qc.cx(i, i + 1)
qc.barrier()
for i in range(5):
    qc.rz(0.5, i)
qc.measure_all()

selector = BackendSelector(backends)

# Get top 3 backends
top_3 = selector.rank_backends(qc, top_n=3)

for rec in top_3:
    print(f"{rec.rank}. {rec.backend.name}")
    print(f"   Score: {rec.score_data.score:.3f}")  # Negative error sum
    print(f"   Compatible: {rec.score_data.compatible}")
    print(f"   Reasons: {rec.score_data.reasons[0]}")

# Set minimum quality threshold
# Since scores are negative, -0.1 means max 10% total error
try:
    high_quality = selector.select_backend(qc, min_score=-0.05)  # Max 5% error
    print(f"High-quality backend: {high_quality.backend.name}")
except ValueError:
    print("No backends met the quality threshold")
```

**Key Concepts:**
- Using `rank_backends()` for full rankings
- Understanding negative error-based scores
- Minimum score filtering with negative thresholds
- Compatibility checking

## Real-World Scenarios

### Scenario 1: Chemistry Circuit with Fractional Gates

VQE and chemistry circuits benefit from fractional gates. The selector detects and reports which configuration is used:

```python
from qiskit.circuit.library import EfficientSU2
from enhanced_quantum_backend_selector import BackendSelector

# Create a typical chemistry ansatz
ansatz = EfficientSU2(num_qubits=4, reps=2)
ansatz.measure_all()

print(f"Circuit depth: {ansatz.depth()}")
print(f"Operations: {ansatz.count_ops()}")

# Selector detects fractional gates from backend properties
selector = BackendSelector(backends)
rec = selector.select_backend(ansatz)

print(f"Best backend: {rec.backend.name}")
print(f"Score: {rec.score_data.score:.4f}")
print(f"Expected error: {-rec.score_data.score * 100:.2f}%")

# Check which gate configuration was detected
for reason in rec.score_data.reasons:
    if 'fractional' in reason.lower() or 'standard' in reason.lower():
        print(f"Configuration: {reason}")
```

**Tip**: To compare fractional vs standard gates, include both versions in your backends list:
```python
backends = [
    service.backend('ibm_torino'),  # Standard
    service.backend('ibm_torino', use_fractional_gates=True),  # Fractional
]
```

### Scenario 2: VQE Algorithm

Variational Quantum Eigensolver requires high-fidelity gates:

```python
from qiskit import QuantumCircuit
from enhanced_quantum_backend_selector import BackendSelector

# Create VQE ansatz
def create_vqe_circuit(num_qubits=4):
    qc = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        qc.ry(0.1 * i, i)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc

qc = create_vqe_circuit(4)

# Select backend - transpilation reveals best backend for this circuit
selector = BackendSelector(backends)
rec = selector.select_backend(qc)

print(f"Best VQE backend: {rec.backend.name}")
print(f"Expected error: {-rec.score_data.score:.4f}")  # Convert negative score to error
print(f"Details: {rec.score_data.reasons[0]}")

### Scenario 2: QAOA for Graph Problems

Quantum Approximate Optimization Algorithm needs good connectivity:

```python
# QAOA circuit with many entangling gates
def create_qaoa_circuit(num_qubits=6):
    qc = QuantumCircuit(num_qubits)
    
    # Initial superposition
    for i in range(num_qubits):
        qc.h(i)
    
    # Problem Hamiltonian (random graph edges)
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)]
    for i, j in edges:
        qc.cx(i, j)
        qc.rz(0.5, j)
        qc.cx(i, j)
    
    qc.measure_all()
    return qc

qc = create_qaoa_circuit(6)

# Transpilation finds backends with topology matching the circuit
rec = selector.select_backend(qc)
print(f"Best QAOA backend: {rec.backend.name}")
print(f"Score: {rec.score_data.score:.3f}")
print(f"Connectivity: {rec.metrics.num_edges} edges")
```

### Scenario 3: Rapid Prototyping

Quick iteration during development:

```python
# Simple test circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Use default scoring (optimized for quality)
rec = selector.select_backend(qc)
print(f"Best backend: {rec.backend.name}")
print(f"Score: {rec.score_data.score:.3f}")  # Negative error sum
print(f"Expected error: {-rec.score_data.score:.2%}")  # As percentage
```

### Scenario 4: Production Workload

Robust backend selection with error handling:

```python
def production_backend_selection(circuit, backends):
    """Production-ready backend selection with fallbacks."""
    selector = BackendSelector(backends)
    
    try:
        # Get best compatible backend
        rec = selector.select_backend(
            circuit,
            require_compatible=True,
        )
        
        # Check if error rate is acceptable (< 10%)
        if -rec.score_data.score < 0.10:
            return rec.backend, "optimal"
        else:
            return rec.backend, "acceptable"
    
    except ValueError as e:
        # No compatible backends found
        print(f"Warning: {e}")
        # Get all backends and pick highest scoring
        all_recs = selector.rank_backends(circuit)
        return all_recs[0].backend, "fallback"

# Use in production
backend, quality = production_backend_selection(qc, backends)
print(f"Selected: {backend.name} (quality: {quality})")
```

### Scenario 5: Batch Processing

Optimize backend selection across multiple circuits:

```python
from typing import Dict, List

def batch_backend_selection(
    circuits: List[QuantumCircuit],
    backends: List,
) -> Dict[int, BackendRecommendation]:
    """Select backends for a batch of circuits."""
    selector = BackendSelector(backends)
    
    recommendations = {}
    
    for i, circuit in enumerate(circuits):
        rec = selector.select_backend(circuit)
        recommendations[i] = rec
        error_pct = -rec.score_data.score * 100
        print(f"Circuit {i}: {rec.backend.name} ")
        print(f"  Score: {rec.score_data.score:.3f} (expected error: {error_pct:.2f}%)")
    
    return recommendations

# Create multiple circuits
circuits = [
    create_vqe_circuit(4),
    create_qaoa_circuit(6),
    QuantumCircuit(3),  # Simple circuit
]

# Select backends for all circuits
results = batch_backend_selection(circuits, backends)
```

## Interactive Examples

### Compare All Backends

```python
def compare_backends(circuit, backends, top_n=5):
    """Compare top backends for a circuit."""
    selector = BackendSelector(backends)
    
    recommendations = selector.rank_backends(circuit, top_n=top_n)
    
    print(f"Circuit: {circuit.num_qubits} qubits, depth {circuit.depth()}\n")
    print(f"{'Rank':<6} {'Backend':<25} {'Score':>10} {'Error %':>10} {'Qubits':>8}")
    print("-" * 65)
    
    for rec in recommendations:
        error_pct = -rec.score_data.score * 100
        print(f"#{rec.rank:<5} {rec.backend.name:<25} "
              f"{rec.score_data.score:>10.4f} {error_pct:>9.2f}% {rec.metrics.num_qubits:>8}")

# Run comparison
qc = create_vqe_circuit(5)
compare_backends(qc, backends)
```

### Analyze Backend Recommendation

```python
def analyze_backend(recommendation):
    """Detailed analysis of a backend recommendation."""
    print("=" * 70)
    print(f"Backend Analysis: {recommendation.backend.name}")
    print("=" * 70)
    
    # Overall score and error
    score = recommendation.score_data.score
    error_pct = -score * 100
    print(f"\nScore: {score:.4f} (Rank #{recommendation.rank})")
    print(f"Expected Error: {error_pct:.2f}%")
    print(f"Compatible: {recommendation.score_data.compatible}")
    
    # Backend specifications
    print("\nBackend Metrics:")
    print(f"  Qubits:          {recommendation.metrics.num_qubits}")
    print(f"  Connectivity:    {recommendation.metrics.num_edges} edges")
    if recommendation.metrics.avg_t1:
        print(f"  Avg T1:          {recommendation.metrics.avg_t1:.2e} s")
    if recommendation.metrics.avg_t2:
        print(f"  Avg T2:          {recommendation.metrics.avg_t2:.2e} s")
    if recommendation.metrics.avg_readout_error is not None:
        print(f"  Readout Error:   {recommendation.metrics.avg_readout_error:.4f}")
    print(f"  Operational:     {recommendation.metrics.operational}")
    
    # Reasons for selection
    if recommendation.score_data.reasons:
        print("\nSelection Reasons:")
        for reason in recommendation.score_data.reasons:
            print(f"  • {reason}")

# Analyze a recommendation
rec = selector.select_backend(qc)
analyze_backend(rec)
```

## Next Steps

- [User Guide](user-guide.md) - Learn about all features in detail
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - System design and patterns
