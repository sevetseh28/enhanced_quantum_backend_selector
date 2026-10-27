# User Guide

This guide covers all features of the Enhanced Quantum Backend Selector.

## How It Works

The library provides intelligent backend selection through **transpilation-based error analysis**:

1. **Transpiles** your circuit to each backend's native gate set
2. **Calculates** the total expected error from all gates, readouts and idle time on the
   qubits used
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
print(f"Score: {rec.score_data.score:.3f}")  # Success probability, 0 to 1
print(f"Expected error: {1 - rec.score_data.score:.2%}")

# Human-readable reasons
for reason in rec.score_data.reasons:
    print(f"  • {reason}")
```

**Score interpretation:**

- Score is the estimated success probability (ESP), between 0 and 1: `0.98` means a 98% chance the circuit runs without error
- Incompatible backends (too few qubits, offline, or transpilation failed) have `compatible=False` and a score of `0`
- Pass `seed=` to `BackendSelector` for reproducible scores
- **Higher scores are better**: `0.99` (1% error) is better than `0.95` (5% error)

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
# Require at least a 90% success probability (at most 10% error)
try:
    rec = selector.select_backend(qc, min_score=0.9)
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

### Parallel Processing

Multiple backends are scored in parallel (up to 10 workers) automatically.

### What to Expect

Transpilation dominates the run time; scoring a transpiled circuit takes milliseconds
(about 0.1 s for a 120-qubit QFT with ~46,000 operations).
Measured on a 12-core laptop with Qiskit's fake IBM devices (127-156 qubits), seeded,
3 transpilation runs per backend:

| Circuit | 1 backend | 10 backends |
|---|---|---|
| GHZ, 100 qubits | < 0.1 s | 0.3 s |
| QFT, 20 qubits | < 0.1 s | 0.8 s |
| QFT, 60 qubits | 1.1 s | 4.7 s |
| QFT, 120 qubits | 0.7 s | 9.4 s |
| EfficientSU2 (full entanglement), 40 qubits x 5 reps | 0.7 s | 9.7 s |

With real IBM backends, add the time to fetch each backend's calibration data and
status. Use `transpilation_runs=1` when speed matters more than stability.

## Limitations

The score is an estimate built from the backend's reported calibration data. Keep these
in mind when comparing backends:

- **Independent errors only.** The success probability multiplies `(1 - error)` for
  every gate and readout, assuming errors are independent. Crosstalk and correlated
  errors are not modelled.
- **Idle error is approximate.** Each qubit's idle time (waiting on other qubits, or
  explicit delays) is charged decoherence from its T1/T2, assuming the circuit is
  scheduled as late as possible. Dynamical decoupling, which suppresses idle error, is
  not modelled, so with it enabled idle error is overestimated. Backends that don't
  report gate durations or T1/T2 get no idle error.
- **Readout counted for every used qubit**, even if the circuit doesn't measure it.
  This matches Estimator-style workloads, which measure all active qubits.
- **Queue time is ignored.** The best-scoring backend may have the longest queue.
- **Your transpilation may differ.** Backends are scored with `optimization_level=2`.
  If you transpile with different settings or your own pass manager, the circuit you
  run can use different qubits than the one that was scored.
- **Broken couplers.** Some devices report gates with an error of 1.0. If the
  transpiler routes through one, the success probability for that run is effectively
  zero. On circuits large enough that every run does this, all backends score about
  `0` and the ranking reflects which backend needs the fewest broken gates, which
  is a weak signal.
- **Missing calibration data** is filled in with the mean error of the same gate on
  that device; gates with no data anywhere count as error-free and are listed in the
  score's `reasons`.
- **Calibration data changes.** Scores reflect the calibration at the time of the call.
  Re-run the selection rather than caching results for long.

## Best Practices

### 1. Handle Exceptions

```python
try:
    rec = selector.select_backend(qc)
except RuntimeError as e:
    # No backend can run the circuit, or none met min_score
    print(f"Selection failed: {e}")
```

### 2. Validate Recommendations

```python
rec = selector.select_backend(qc)

# Check error rate
error_pct = (1 - rec.score_data.score) * 100
if error_pct > 10:
    print(f"Warning: {error_pct:.1f}% expected error")
```

### 3. Compare Multiple Backends

```python
top_5 = selector.rank_backends(qc, top_n=5)

for rec in top_5:
    error_pct = (1 - rec.score_data.score) * 100
    print(f"#{rec.rank}: {rec.backend.name} - {error_pct:.2f}% error")
```

## Example: Production Backend Selection

```python
def select_production_backend(circuit, backends):
    """Select backend with error handling."""
    selector = BackendSelector(backends)

    try:
        rec = selector.select_backend(circuit, require_compatible=True)

        error_pct = (1 - rec.score_data.score) * 100
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
```

## Next Steps

- [Examples](examples.md) - More code examples
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - System design details
