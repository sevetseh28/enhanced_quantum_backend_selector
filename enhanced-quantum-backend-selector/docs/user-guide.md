# User Guide

This guide covers all features of the Enhanced Quantum Backend Selector.

## How It Works

The library provides intelligent backend selection through **transpilation-based error analysis**:

1. **Transpiles** your circuit to each backend's native gate set
2. **Calculates** the total expected error from all gates and qubits used
3. **Averages** over multiple transpilation runs for stability (default: 3)
4. **Ranks** backends by their actual expected error

## Basic Usage

```python
from enhanced_quantum_backend_selector import BackendSelector
from qiskit import QuantumCircuit

selector = BackendSelector(backends)
rec = selector.select_backend(circuit)
backend = rec.backend
```

## Understanding Scores

The score is based on **transpilation-based error estimation**:

```python
rec = selector.select_backend(qc)

print(f"Backend: {rec.backend.name}")
print(f"Score: {rec.score_data.score:.3f}")  # Negative expected error
print(f"Expected error: {-rec.score_data.score:.2%}")

# Human-readable reasons
for reason in rec.score_data.reasons:
    print(f"  • {reason}")
```

**Score interpretation:**

- Score is the negative expected error: `score = -(1 - ESP)`, between -1 and 0
- Incompatible backends (too few qubits, offline, or transpilation failed) have `compatible=False` and a score of `-inf`
- Pass `seed=` to `BackendSelector` for reproducible scores
- **Higher scores are better** (less negative = lower error)
- `-0.01` (1% error) is better than `-0.05` (5% error)

## Advanced Features

### Get Full Rankings

```python
# Get all backends ranked
all_rankings = selector.rank_backends(qc)

for rec in all_rankings:
    print(f"{rec.rank}. {rec.backend.name}: {rec.score_data.score:.3f}")

# Get only top N
top_3 = selector.rank_backends(qc, top_n=3)
```

### Minimum Score Filtering

```python
# Require max 10% total error
try:
    rec = selector.select_backend(qc, min_score=-0.1)
except RuntimeError as e:
    print(f"No backends met threshold: {e}")
```

### Compatibility Filtering

```python
# Strict mode (default) - only compatible backends
rec = selector.select_backend(qc, require_compatible=True)

# Lenient mode - include incompatible backends in ranking
rec = selector.select_backend(qc, require_compatible=False)
```

### Configuring Transpilation Runs

```python
# Default: 3 runs (balanced)
selector = BackendSelector(backends)

# Fast: 1 run
selector_fast = BackendSelector(backends, transpilation_runs=1)

# Accurate: 5 runs
selector_accurate = BackendSelector(backends, transpilation_runs=5)
```

### Fractional Gates for Chemistry

For chemistry and VQE circuits, fractional gates can improve results:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()

# Include both versions to compare
backends = [
    service.backend('ibm_torino'),
    service.backend('ibm_torino', use_fractional_gates=True),
]

selector = BackendSelector(backends)
rec = selector.select_backend(chemistry_circuit)
```

## Performance

### Caching

Backend analyzers are cached per-selector instance:

```python
# First call creates analyzer
rec1 = selector.select_backend(qc1)

# Second call reuses cached analyzer
rec2 = selector.select_backend(qc2)

# Clear cache to force fresh analysis
selector.clear_cache()
```

### Parallel Processing

Multiple backends are scored in parallel (up to 10 workers) automatically.

## Best Practices

### 1. Handle Exceptions

```python
try:
    rec = selector.select_backend(qc)
except ValueError as e:
    print(f"Selection failed: {e}")
    # Fallback logic
```

### 2. Validate Recommendations

```python
rec = selector.select_backend(qc)

# Check error rate
error_pct = -rec.score_data.score * 100
if error_pct > 10:
    print(f"Warning: {error_pct:.1f}% expected error")
```

### 3. Compare Multiple Backends

```python
top_5 = selector.rank_backends(qc, top_n=5)

for rec in top_5:
    error_pct = -rec.score_data.score * 100
    print(f"#{rec.rank}: {rec.backend.name} - {error_pct:.2f}% error")
```

## Example: Production Backend Selection

```python
def select_production_backend(circuit, backends):
    """Select backend with error handling."""
    selector = BackendSelector(backends)

    try:
        rec = selector.select_backend(circuit, require_compatible=True)

        error_pct = -rec.score_data.score * 100
        if error_pct < 10:
            return rec.backend, "optimal"
        else:
            return rec.backend, "acceptable"

    except ValueError:
        # Fallback to first available
        rankings = selector.rank_backends(circuit)
        return rankings[0].backend, "fallback"
```

## Next Steps

- [Examples](examples.md) - More code examples
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - System design details
