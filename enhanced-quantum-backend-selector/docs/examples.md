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

This example shows advanced features and strategies:

```python
from enhanced_quantum_backend_selector import BackendSelector, ScoringWeights

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

# Strategy 1: Quality-First
quality_weights = ScoringWeights(
    gate_fidelity_weight=2.0,
    connectivity_weight=1.5,
    coherence_weight=1.5,
    queue_weight=0.2,
)
quality_rec = selector.select_backend(qc, weights=quality_weights)

# Strategy 2: Speed-First
speed_weights = ScoringWeights(
    gate_fidelity_weight=0.5,
    connectivity_weight=0.8,
    coherence_weight=0.5,
    queue_weight=3.0,
)
speed_rec = selector.select_backend(qc, weights=speed_weights)

# Compare strategies
print(f"Quality: {quality_rec.backend.name} ({quality_rec.score_data.score:.3f})")
print(f"Speed:   {speed_rec.backend.name} ({speed_rec.score_data.score:.3f})")
```

**Key Concepts:**
- Creating custom `ScoringWeights`
- Comparing different optimization strategies
- Using `rank_backends()` for full rankings
- Minimum score filtering
- Compatibility checking

## Real-World Scenarios

### Scenario 1: VQE Algorithm

Variational Quantum Eigensolver requires high-fidelity gates:

```python
from qiskit import QuantumCircuit
from enhanced_quantum_backend_selector import BackendSelector, ScoringWeights

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

# Select backend prioritizing fidelity and coherence
selector = BackendSelector(backends)
vqe_weights = ScoringWeights(
    gate_fidelity_weight=2.5,    # Critical for VQE
    connectivity_weight=1.0,
    coherence_weight=2.0,         # Long coherence needed
    queue_weight=0.3,
)

rec = selector.select_backend(qc, weights=vqe_weights)
print(f"Best VQE backend: {rec.backend.name}")
```

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

# Prioritize connectivity
qaoa_weights = ScoringWeights(
    gate_fidelity_weight=1.5,
    connectivity_weight=2.5,      # Critical for QAOA
    coherence_weight=1.2,
    queue_weight=0.5,
)

rec = selector.select_backend(qc, weights=qaoa_weights)
print(f"Best QAOA backend: {rec.backend.name}")
print(f"Coupling edges: {len(rec.metrics.coupling_map)}")
```

### Scenario 3: Rapid Prototyping

Quick iteration during development:

```python
# Simple test circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Prioritize speed
prototype_weights = ScoringWeights(
    gate_fidelity_weight=0.3,
    connectivity_weight=0.5,
    coherence_weight=0.3,
    queue_weight=3.0,             # Get results fast
)

rec = selector.select_backend(qc, weights=prototype_weights)
print(f"Fast backend: {rec.backend.name}")
print(f"Queue score: {rec.score_data.queue_score:.3f}")
```

### Scenario 4: Production Workload

Balanced approach for production:

```python
def production_backend_selection(circuit, backends):
    """Production-ready backend selection with fallbacks."""
    selector = BackendSelector(backends)
    
    # Balanced production weights
    prod_weights = ScoringWeights(
        gate_fidelity_weight=1.5,
        connectivity_weight=1.2,
        coherence_weight=1.0,
        queue_weight=0.8,
    )
    
    try:
        # First attempt: strict requirements
        rec = selector.select_backend(
            circuit,
            weights=prod_weights,
            require_compatible=True,
            min_score=0.5,
        )
        return rec.backend, "optimal"
    
    except ValueError:
        # Second attempt: lower threshold
        try:
            rec = selector.select_backend(
                circuit,
                weights=prod_weights,
                require_compatible=True,
                min_score=0.3,
            )
            return rec.backend, "acceptable"
        
        except ValueError:
            # Final fallback: any compatible backend
            rec = selector.select_backend(
                circuit,
                require_compatible=True,
            )
            return rec.backend, "fallback"

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
    strategy: str = "balanced"
) -> Dict[int, BackendRecommendation]:
    """Select backends for a batch of circuits."""
    selector = BackendSelector(backends)
    
    # Define strategies
    strategies = {
        "quality": ScoringWeights(2.0, 1.5, 1.5, 0.2),
        "speed": ScoringWeights(0.5, 0.8, 0.5, 3.0),
        "balanced": ScoringWeights(),
    }
    
    weights = strategies[strategy]
    recommendations = {}
    
    for i, circuit in enumerate(circuits):
        rec = selector.select_backend(circuit, weights=weights)
        recommendations[i] = rec
        print(f"Circuit {i}: {rec.backend.name} (score: {rec.score_data.score:.3f})")
    
    return recommendations

# Create multiple circuits
circuits = [
    create_vqe_circuit(4),
    create_qaoa_circuit(6),
    QuantumCircuit(3),  # Simple circuit
]

# Select backends for all circuits
results = batch_backend_selection(circuits, backends, strategy="balanced")
```

## Interactive Examples

### Compare All Strategies

```python
def compare_strategies(circuit, backends):
    """Compare different weight strategies for a circuit."""
    selector = BackendSelector(backends)
    
    strategies = {
        "Quality-First": ScoringWeights(2.0, 1.5, 1.5, 0.2),
        "Speed-First": ScoringWeights(0.5, 0.8, 0.5, 3.0),
        "Connectivity-First": ScoringWeights(1.0, 3.0, 1.0, 0.5),
        "Balanced": ScoringWeights(),
    }
    
    print(f"Circuit: {circuit.num_qubits} qubits, depth {circuit.depth()}\n")
    print(f"{'Strategy':<20} {'Backend':<25} {'Score':>8} {'Qubits':>8}")
    print("-" * 66)
    
    for name, weights in strategies.items():
        rec = selector.select_backend(circuit, weights=weights)
        print(f"{name:<20} {rec.backend.name:<25} "
              f"{rec.score_data.score:>8.3f} {rec.metrics.num_qubits:>8}")

# Run comparison
qc = create_vqe_circuit(5)
compare_strategies(qc, backends)
```

### Analyze Score Breakdown

```python
def analyze_backend(recommendation):
    """Detailed analysis of a backend recommendation."""
    print("=" * 70)
    print(f"Backend Analysis: {recommendation.backend.name}")
    print("=" * 70)
    
    print(f"\nOverall Score: {recommendation.score_data.score:.3f} (Rank #{recommendation.rank})")
    
    print("\nScore Breakdown:")
    components = [
        ("Gate Fidelity", recommendation.score_data.gate_fidelity_score),
        ("Connectivity", recommendation.score_data.connectivity_score),
        ("Coherence", recommendation.score_data.coherence_score),
        ("Queue Time", recommendation.score_data.queue_score),
    ]
    
    for name, score in components:
        bar = "█" * int(score * 20)
        print(f"  {name:<15} {score:.3f} {bar}")
    
    print("\nBackend Metrics:")
    print(f"  Qubits:          {recommendation.metrics.num_qubits}")
    print(f"  Coupling Edges:  {len(recommendation.metrics.coupling_map)}")
    print(f"  Avg T1:          {recommendation.metrics.t1_avg:.2e} s")
    print(f"  Avg T2:          {recommendation.metrics.t2_avg:.2e} s")
    print(f"  Readout Error:   {recommendation.metrics.readout_error_avg:.4f}")
    print(f"  Operational:     {recommendation.metrics.operational}")
    
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
- [Best Practices](user-guide/best-practices.md) - Production tips and patterns
