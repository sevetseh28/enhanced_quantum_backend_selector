# User Guide

This guide covers all features of the Enhanced Quantum Backend Selector and how to use them effectively.

## Overview

The library provides intelligent backend selection through multi-criteria analysis. Instead of simply choosing the least busy backend, it considers:

1. **Gate Fidelity** - Quality of quantum operations
2. **Connectivity** - Topology match with circuit requirements
3. **Coherence** - T1/T2 times relative to circuit depth
4. **Availability** - Queue depth and operational status

## Basic Usage

### Initialize the Selector

```python
from enhanced_quantum_backend_selector import BackendSelector
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backends = service.backends()

selector = BackendSelector(backends)
```

### Select a Backend

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

recommendation = selector.select_backend(qc)
backend = recommendation.backend
```

## Understanding Scores

### Overall Score

The score is based on **transpilation-based error estimation**:

1. **Circuit is transpiled** to the backend's native gate set with optimization level 2
2. **Total error is calculated** by summing errors for all qubits used in the transpiled circuit:
   - Single-qubit gate errors
   - Two-qubit gate errors
   - Readout errors
3. **Score is averaged** over 3 independent transpilation runs
4. **Score is negative** of the total error: `score = -total_error`

**Higher scores are better** (less negative = lower error):
- Score of `-0.01` is better than `-0.05`
- Lower error means higher quality execution

### Why Transpilation-Based?

Transpiling the circuit to the backend reveals:
- Which specific qubits will be used
- Exact gate decompositions needed
- Real error rates for the actual execution path

This provides a more accurate quality estimate than generic backend metrics.

### Multiple Transpilation Runs

Transpilation can produce different qubit layouts. Running 3 times and averaging:
- Accounts for layout variation
- Provides more stable scoring
- Reduces sensitivity to single unlucky transpilations

### Interpreting Results

```python
rec = selector.select_backend(qc)

print(f"Backend: {rec.backend.name}")
print(f"Score: {rec.score_data.score:.3f}")  # Negative error sum
print(f"Compatible: {rec.score_data.compatible}")

# Human-readable reasons
for reason in rec.score_data.reasons:
    print(f"  • {reason}")
```

**Example output:**
```
Backend: ibm_kyoto
Score: -0.0234  # Total error ~2.34%
Compatible: True
  • Total error on 5 qubits: 2.341234%
  • Used qubits: [0, 1, 14, 15, 18]
  • Average score over 3 transpilation runs: -0.023412
```

## Scoring Weights (Future Feature)

The `ScoringWeights` class is available for API compatibility but **not currently used** in the transpilation-based scoring system.

The current implementation:
- Transpiles circuits to each backend
- Calculates total error from the transpiled circuit
- Returns negative error sum as the score

Future versions may incorporate weighted multi-criteria scoring alongside transpilation-based scoring. The `weights` parameter is accepted but has no effect on the current scoring calculation.

```python
from enhanced_quantum_backend_selector import ScoringWeights

# Available for API compatibility, but not used in scoring
weights = ScoringWeights(
    gate_fidelity_weight=1.5,
    connectivity_weight=1.0,
    coherence_weight=0.8,
    queue_weight=0.4,
)

rec = selector.select_backend(qc, weights=weights)  # weights parameter accepted but ignored
```

## Advanced Features

### Get Full Rankings

Compare all backends:

```python
# Get all backends ranked
all_rankings = selector.rank_backends(qc)

for rec in all_rankings:
    print(f"{rec.rank}. {rec.backend.name}: {rec.score_data.score:.3f}")

# Get only top N
top_3 = selector.rank_backends(qc, top_n=3)
```

### Minimum Score Filtering

Require backends to meet a quality threshold:

```python
# Since scores are negative errors, use negative thresholds
# -0.1 means max 10% total error, -0.05 means max 5% error
try:
    rec = selector.select_backend(qc, min_score=-0.1)  # Max 10% error
    print(f"Selected: {rec.backend.name}")
    print(f"Score: {rec.score_data.score:.3f}")
except ValueError as e:
    print(f"No backends met minimum score: {e}")
```

**Note:** Remember scores are negative. A higher (less negative) score is better:
- `-0.01` passes `min_score=-0.05` threshold ✓
- `-0.08` fails `min_score=-0.05` threshold ✗

### Compatibility Checking

Control whether backends must support your circuit:

```python
# Strict (default) - only compatible backends
strict_rec = selector.select_backend(qc, require_compatible=True)

# Lenient - allow incompatible backends
# (they'll have lower scores but won't be rejected)
lenient_rec = selector.select_backend(qc, require_compatible=False)
```

### Combining Options

All options can be combined:

```python
rec = selector.select_backend(
    circuit=qc,
    weights=quality_weights,
    top_n=5,                    # Consider only top 5
    require_compatible=True,     # Must support circuit
    min_score=0.3,              # Minimum acceptable score
)
```

## Performance Optimization

### Caching

Backend metrics are cached for 1 hour to minimize API calls:

```python
# First call queries backends
rec1 = selector.select_backend(qc1)

# Second call uses cached data (if within 1 hour)
rec2 = selector.select_backend(qc2)

# Cache is per-selector instance
# Create new selector to bypass cache
selector2 = BackendSelector(backends)
```

### Parallel Processing

Multiple backends are scored in parallel (up to 10 workers):

```python
# Automatically uses ThreadPoolExecutor
# No configuration needed
selector = BackendSelector(backends)  # All backends scored in parallel
```

## Best Practices

### 1. Choose Appropriate Weights

Match weights to your use case:

- **Research/Publications**: Quality-first (high fidelity, coherence)
- **Rapid Prototyping**: Speed-first (high queue weight)
- **Complex Circuits**: Connectivity-first (high connectivity weight)
- **Production**: Balanced (default weights)

### 2. Handle Exceptions

Always handle potential errors:

```python
try:
    rec = selector.select_backend(qc)
    backend = rec.backend
except ValueError as e:
    # No compatible backends found
    print(f"Selection failed: {e}")
    # Fallback logic
    backend = least_busy(backends)
```

### 3. Validate Recommendations

Check the score and reasons:

```python
rec = selector.select_backend(qc)

# Check if score is acceptable
if rec.score_data.score < 0.3:
    print("Warning: Low quality backend selected")

# Review reasons
print("Selection reasons:")
for reason in rec.score_data.reasons:
    print(f"  • {reason}")
```

### 4. Compare Multiple Strategies

Test different weight configurations:

```python
strategies = {
    "Quality": quality_weights,
    "Speed": speed_weights,
    "Balanced": ScoringWeights(),  # defaults
}

for name, weights in strategies.items():
    rec = selector.select_backend(qc, weights=weights)
    print(f"{name}: {rec.backend.name} ({rec.score_data.score:.3f})")
```

### 5. Monitor Backend Status

Backend properties can change:

```python
# Get fresh metrics
selector = BackendSelector(backends)
rec = selector.select_backend(qc)

# Check backend status
if not rec.metrics.operational:
    print("Warning: Selected backend is not operational")
```

## Example Workflows

### Production Pipeline

```python
from enhanced_quantum_backend_selector import BackendSelector, ScoringWeights

def select_production_backend(circuit, backends):
    """Select backend for production workload."""
    selector = BackendSelector(backends)
    
    # Balanced weights with quality preference
    weights = ScoringWeights(
        gate_fidelity_weight=1.5,
        connectivity_weight=1.2,
        coherence_weight=1.0,
        queue_weight=0.6,
    )
    
    try:
        rec = selector.select_backend(
            circuit,
            weights=weights,
            require_compatible=True,
            min_score=0.4,
        )
        return rec.backend
    except ValueError:
        # Fallback to least busy
        return least_busy(backends)
```

### Research Experiment

```python
def select_research_backend(circuit, backends):
    """Select highest quality backend for research."""
    selector = BackendSelector(backends)
    
    # Maximum quality
    weights = ScoringWeights(
        gate_fidelity_weight=2.0,
        connectivity_weight=1.5,
        coherence_weight=1.8,
        queue_weight=0.1,
    )
    
    rankings = selector.rank_backends(circuit, weights=weights)
    
    # Report top 3 for comparison
    print("Top 3 backends for research:")
    for rec in rankings[:3]:
        print(f"  {rec.rank}. {rec.backend.name}: {rec.score_data.score:.3f}")
    
    return rankings[0].backend
```

### Batch Job Optimization

```python
def select_backends_for_batch(circuits, backends, strategy="balanced"):
    """Select optimal backends for multiple circuits."""
    selector = BackendSelector(backends)
    
    strategies = {
        "quality": ScoringWeights(2.0, 1.5, 1.5, 0.2),
        "speed": ScoringWeights(0.5, 0.8, 0.5, 3.0),
        "balanced": ScoringWeights(),
    }
    
    weights = strategies[strategy]
    selections = {}
    
    for i, circuit in enumerate(circuits):
        rec = selector.select_backend(circuit, weights=weights)
        selections[f"circuit_{i}"] = {
            "backend": rec.backend.name,
            "score": rec.score_data.score,
            "rank": rec.rank,
        }
    
    return selections
```

## Next Steps

- [Examples](examples.md) - Practical code examples and use cases
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - Design and implementation details
