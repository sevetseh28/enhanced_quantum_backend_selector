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

The overall score is a weighted combination of four component scores:

```python
score = (
    fidelity_score * fidelity_weight +
    connectivity_score * connectivity_weight +
    coherence_score * coherence_weight +
    queue_score * queue_weight
)
```

Higher scores indicate better backends for the given circuit.

### Score Components

Each component is normalized to [0, 1]:

**Gate Fidelity Score** - Based on error rates:
- Single-qubit gate errors
- Two-qubit gate errors  
- Readout errors

**Connectivity Score** - Based on topology match:
- Number of edges in coupling map
- Compatibility with circuit connectivity requirements

**Coherence Score** - Based on decoherence times:
- T1 (relaxation) times
- T2 (dephasing) times
- Relative to circuit depth

**Queue Score** - Based on availability:
- Pending jobs in queue
- Operational status

### Interpreting Results

```python
rec = selector.select_backend(qc)

print(f"Overall Score: {rec.score_data.score:.3f}")
print("\nBreakdown:")
print(f"  Fidelity:     {rec.score_data.gate_fidelity_score:.3f}")
print(f"  Connectivity: {rec.score_data.connectivity_score:.3f}")
print(f"  Coherence:    {rec.score_data.coherence_score:.3f}")
print(f"  Queue:        {rec.score_data.queue_score:.3f}")

# Human-readable reasons
for reason in rec.score_data.reasons:
    print(f"  • {reason}")
```

## Custom Scoring Weights

Adjust weights based on your priorities:

### Default Weights

```python
from enhanced_quantum_backend_selector import ScoringWeights

# These are the defaults
default_weights = ScoringWeights(
    gate_fidelity_weight=1.5,   # Highest priority
    connectivity_weight=1.0,     # High priority
    coherence_weight=0.8,        # Moderate priority
    queue_weight=0.4,            # Lower priority
)
```

### Quality-First Strategy

Prioritize result quality over execution time:

```python
quality_weights = ScoringWeights(
    gate_fidelity_weight=2.0,   # Very high
    connectivity_weight=1.5,     # High
    coherence_weight=1.5,        # High
    queue_weight=0.2,            # Very low - don't care about waiting
)

rec = selector.select_backend(qc, weights=quality_weights)
```

### Speed-First Strategy

Get results as quickly as possible:

```python
speed_weights = ScoringWeights(
    gate_fidelity_weight=0.5,    # Lower
    connectivity_weight=0.8,     # Moderate
    coherence_weight=0.5,        # Lower
    queue_weight=3.0,            # Very high - minimize wait time
)

rec = selector.select_backend(qc, weights=speed_weights)
```

### Connectivity-First Strategy

For circuits with complex coupling requirements:

```python
connectivity_weights = ScoringWeights(
    gate_fidelity_weight=1.0,
    connectivity_weight=3.0,     # Very high
    coherence_weight=1.0,
    queue_weight=0.5,
)

rec = selector.select_backend(qc, weights=connectivity_weights)
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
try:
    rec = selector.select_backend(qc, min_score=0.5)
    print(f"Selected: {rec.backend.name}")
except ValueError as e:
    print(f"No backends met minimum score: {e}")
```

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

- [Scoring Weights Guide](user-guide/scoring-weights.md) - Deep dive into weight configuration
- [Backend Selection Guide](user-guide/backend-selection.md) - Advanced selection strategies
- [Best Practices](user-guide/best-practices.md) - Production tips and patterns
- [API Reference](api-reference.md) - Complete API documentation
