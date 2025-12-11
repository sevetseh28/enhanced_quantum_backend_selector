# Quickstart Guide: Transpiled Circuit Error-Based Scoring

**Feature**: `002-transpiled-error-scoring`  
**Date**: December 11, 2025  
**Status**: Phase 1 Design

## Overview

This quickstart guide demonstrates how to use the transpiled circuit error-based scoring feature for quantum backend selection. It covers:
1. Basic usage (backward compatible)
2. Custom configuration
3. Advanced scenarios
4. Migration guide from old API
5. Error handling

---

## Installation

```bash
# Install from PyPI (when released)
pip install enhanced-quantum-backend-selector

# Or install from source
cd enhanced-quantum-backend-selector
poetry install
```

**Requirements**:
- Python 3.10+
- Qiskit 2.0+
- qiskit-ibm-runtime

---

## Basic Usage (Backward Compatible)

### Example 1: Select Best Backend (Default Configuration)

```python
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService
from enhanced_quantum_backend_selector import BackendSelector

# Create service
service = QiskitRuntimeService(channel="ibm_quantum")

# Create circuit
circuit = QuantumCircuit(3)
circuit.h(0)
circuit.cx(0, 1)
circuit.cx(1, 2)
circuit.measure_all()

# Select best backend (uses transpiled scoring by default)
selector = BackendSelector(service)
best_backend = selector.select_backend(circuit)

print(f"Best backend: {best_backend.backend.name}")
print(f"Score: {best_backend.score_data.total_score:.4f}")
print(f"Rank: {best_backend.rank}")

# NEW: Access transpilation details
if best_backend.transpilation_details:
    details = best_backend.transpilation_details
    print(f"\nTranspilation Details:")
    print(f"  Final score (error sum): {details.final_score:.6f}")
    print(f"  Aggregation method: {details.aggregation_method}")
    print(f"  Successful runs: {details.successful_runs}/{details.successful_runs + details.failed_runs}")
    print(f"  Individual scores: {[f'{s:.6f}' for s in details.individual_scores]}")
    if details.variance:
        print(f"  Variance: {details.variance:.6f}")
```

**Output Example**:
```
Best backend: ibm_brisbane
Score: 0.8542
Rank: 1

Transpilation Details:
  Final score (error sum): 0.024703
  Aggregation method: mean
  Successful runs: 3/3
  Individual scores: ['0.024703', '0.024703', '0.024703']
  Variance: 0.000000
```

---

### Example 2: Rank All Backends

```python
# Rank all available backends
ranked_backends = selector.rank_backends(circuit)

print(f"Found {len(ranked_backends)} compatible backends:\n")

for rec in ranked_backends[:5]:  # Top 5
    print(f"{rec.rank}. {rec.backend.name}")
    print(f"   Score: {rec.score_data.total_score:.4f}")
    if rec.transpilation_details:
        print(f"   Transpiled error: {rec.transpilation_details.final_score:.6f}")
        print(f"   Runs: {rec.transpilation_details.successful_runs}/{rec.transpilation_details.successful_runs + rec.transpilation_details.failed_runs}")
    print()
```

**Output Example**:
```
Found 8 compatible backends:

1. ibm_brisbane
   Score: 0.8542
   Transpiled error: 0.024703
   Runs: 3/3

2. ibm_kyoto
   Score: 0.8321
   Transpiled error: 0.026891
   Runs: 3/3

3. ibm_osaka
   Score: 0.8105
   Transpiled error: 0.029124
   Runs: 3/3
```

---

## Custom Configuration

### Example 3: Median Aggregation with 5 Runs

```python
from enhanced_quantum_backend_selector import ScoringConfiguration

# Create custom configuration
config = ScoringConfiguration(
    transpilation_runs=5,          # Run 5 times instead of default 3
    aggregation_method='median',   # Use median instead of mean
    optimization_level=2           # Less aggressive optimization
)

# Use custom config
best = selector.select_backend(circuit, config=config)

print(f"Best backend: {best.backend.name}")
print(f"Median of 5 runs: {best.transpilation_details.final_score:.6f}")
print(f"Individual scores: {[f'{s:.6f}' for s in best.transpilation_details.individual_scores]}")
```

**Output Example**:
```
Best backend: ibm_brisbane
Median of 5 runs: 0.024703
Individual scores: ['0.024550', '0.024703', '0.024703', '0.024890', '0.025012']
```

---

### Example 4: Minimum Error Aggregation

```python
# Conservative approach: pick backend with best single run
config = ScoringConfiguration(
    transpilation_runs=10,         # Many runs to find best
    aggregation_method='minimum'   # Use minimum error
)

best = selector.select_backend(circuit, config=config)

print(f"Best backend: {best.backend.name}")
print(f"Minimum error from 10 runs: {best.transpilation_details.final_score:.6f}")
print(f"Best vs worst: {min(best.transpilation_details.individual_scores):.6f} / {max(best.transpilation_details.individual_scores):.6f}")
```

---

### Example 5: Fractional Gates Configuration

```python
# Try both fractional gates enabled and disabled, pick best
config = ScoringConfiguration(
    fractional_gates_mode='both'  # Default: try both configurations
)

best = selector.select_backend(circuit, config=config)

if best.fractional_gates_used is not None:
    print(f"Best config used fractional gates: {best.fractional_gates_used}")

# Force fractional gates enabled
config_enabled = ScoringConfiguration(
    fractional_gates_mode='enabled'
)
best_fg = selector.select_backend(circuit, config=config_enabled)

# Force fractional gates disabled
config_disabled = ScoringConfiguration(
    fractional_gates_mode='disabled'
)
best_no_fg = selector.select_backend(circuit, config=config_disabled)

print(f"With fractional gates: {best_fg.transpilation_details.final_score:.6f}")
print(f"Without fractional gates: {best_no_fg.transpilation_details.final_score:.6f}")
```

---

## Advanced Usage

### Example 6: Combining with Custom Scoring Weights

```python
from enhanced_quantum_backend_selector import ScoringWeights

# Custom weights for overall scoring
weights = ScoringWeights(
    error_rate=1.0,
    gate_fidelity=0.8,
    readout_fidelity=0.7,
    t1_time=0.5,
    t2_time=0.5
)

# Combine with transpilation config
config = ScoringConfiguration(
    transpilation_runs=3,
    aggregation_method='mean',
    weights=weights  # Include custom weights
)

best = selector.select_backend(circuit, config=config)
print(f"Best backend with custom weights: {best.backend.name}")
```

---

### Example 7: Handling Transpilation Failures

```python
# Circuit that may be too wide for some backends
wide_circuit = QuantumCircuit(127)
wide_circuit.h(range(127))
wide_circuit.measure_all()

try:
    # Some backends may be excluded due to width
    ranked = selector.rank_backends(wide_circuit)
    
    print(f"Compatible backends: {len(ranked)}")
    
    # Check for failures in top backend
    best = ranked[0]
    if best.transpilation_details:
        failed = best.transpilation_details.failed_runs
        if failed > 0:
            print(f"Warning: {failed} transpilations failed for {best.backend.name}")
    
except ValueError as e:
    # All backends failed
    print(f"Error: {e}")
    print("Try reducing circuit width or depth")
```

---

### Example 8: Performance Monitoring

```python
import time

# Monitor transpilation performance
start = time.time()

config = ScoringConfiguration(
    transpilation_runs=3
)

backends_count = len(selector._service.backends())
ranked = selector.rank_backends(circuit, config=config)

elapsed = time.time() - start

print(f"Performance Metrics:")
print(f"  Backends evaluated: {len(ranked)}")
print(f"  Total transpilations: {len(ranked) * config.transpilation_runs}")
print(f"  Total time: {elapsed:.2f}s")
print(f"  Time per backend: {elapsed / len(ranked):.3f}s")
print(f"  Time per transpilation: {elapsed / (len(ranked) * config.transpilation_runs):.3f}s")

# Performance target: < 10 seconds for 20 backends
if elapsed > 10:
    print("⚠️  WARNING: Exceeded 10-second performance target")
else:
    print("✅ PASSED 10-second performance target")
```

**Output Example**:
```
Performance Metrics:
  Backends evaluated: 8
  Total transpilations: 24
  Total time: 0.29s
  Time per backend: 0.036s
  Time per transpilation: 0.012s
✅ PASSED 10-second performance target
```

---

### Example 9: Variance Analysis for Stochastic Transpilation

```python
# When transpiler is stochastic, variance matters
config = ScoringConfiguration(
    transpilation_runs=10,  # More runs to detect variance
    aggregation_method='mean'
)

best = selector.select_backend(circuit, config=config)
details = best.transpilation_details

if details.variance and details.variance > 0.00001:
    print(f"⚠️  High variance detected: {details.variance:.6f}")
    print(f"Standard deviation: {details.std_dev:.6f}")
    print(f"This suggests stochastic transpilation")
    print(f"Consider using 'median' or 'minimum' aggregation")
else:
    print(f"✅ Low variance: {details.variance:.6f}")
    print(f"Transpilation appears deterministic for this circuit")
```

---

## Migration Guide

### From Old API (Pre-Transpilation Scoring)

**Before** (using static backend metrics):
```python
from enhanced_quantum_backend_selector import BackendSelector

selector = BackendSelector(service)
best = selector.select_backend(circuit)
```

**After** (identical API, now uses transpiled scoring by default):
```python
from enhanced_quantum_backend_selector import BackendSelector

selector = BackendSelector(service)
best = selector.select_backend(circuit)  # Same call!

# NEW: Access transpilation details
print(f"Transpiled error sum: {best.transpilation_details.final_score:.6f}")
```

**Changes**:
- ✅ **No code changes required** for basic usage
- ✅ Scoring now based on transpiled circuit (more accurate)
- ✅ New optional field `transpilation_details` available
- ✅ Performance may be slightly slower (but < 10s for 20 backends)

---

### Deprecation Warnings

**Old**: Passing `weights` directly
```python
weights = ScoringWeights(error_rate=1.0)
best = selector.select_backend(circuit, weights=weights)  # Deprecated!
```

**New**: Pass weights via `config`
```python
weights = ScoringWeights(error_rate=1.0)
config = ScoringConfiguration(weights=weights)
best = selector.select_backend(circuit, config=config)  # Recommended
```

The old API still works but will show a deprecation warning in logs.

---

## Error Handling Guide

### Common Errors and Solutions

#### 1. All Backends Failed Transpilation

**Error**:
```python
ValueError: All 8 backends failed transpilation for circuit. Check circuit compatibility or reduce circuit depth.
```

**Solution**:
```python
# Option 1: Reduce circuit complexity
circuit = QuantumCircuit(3)  # Instead of 127 qubits

# Option 2: Lower optimization level
config = ScoringConfiguration(optimization_level=1)

# Option 3: Check backend compatibility manually
for backend in service.backends():
    if backend.num_qubits >= circuit.num_qubits:
        print(f"{backend.name}: {backend.num_qubits} qubits")
```

---

#### 2. Invalid Configuration

**Error**:
```python
ValueError: transpilation_runs must be positive integer, got 0
```

**Solution**:
```python
# Use valid configuration values
config = ScoringConfiguration(
    transpilation_runs=3,            # Must be >= 1
    aggregation_method='mean',       # Must be 'mean', 'median', or 'minimum'
    fractional_gates_mode='both',    # Must be 'both', 'enabled', or 'disabled'
    optimization_level=3             # Must be 0-3
)
```

---

#### 3. Backend Excluded (Partial Failure)

**Warning in logs**:
```
WARNING: Backend ibm_lagos excluded: all 3 transpilations failed. Last error: CircuitTooWideForTarget
```

**Solution**:
```python
# Check which backends were excluded
all_backends_count = len(service.backends())
ranked = selector.rank_backends(circuit)
excluded_count = all_backends_count - len(ranked)

if excluded_count > 0:
    print(f"⚠️  {excluded_count} backends excluded due to transpilation failures")
    print(f"Remaining candidates: {len(ranked)}")

# Still get best available backend
if ranked:
    best = ranked[0]
    print(f"Best available: {best.backend.name}")
```

---

## Testing Your Integration

### Example 10: Validate Transpilation Scoring

```python
def test_transpilation_scoring():
    """Validate that transpilation scoring works correctly."""
    
    # Create test circuit
    circuit = QuantumCircuit(3)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)
    
    selector = BackendSelector(service)
    
    # Test default config
    best = selector.select_backend(circuit)
    assert best.transpilation_details is not None, "Missing transpilation details"
    assert best.transpilation_details.successful_runs >= 1, "No successful runs"
    
    # Test custom config
    config = ScoringConfiguration(
        transpilation_runs=5,
        aggregation_method='median'
    )
    best_custom = selector.select_backend(circuit, config=config)
    assert len(best_custom.transpilation_details.individual_scores) == 5, "Wrong run count"
    assert best_custom.transpilation_details.aggregation_method == 'median', "Wrong method"
    
    print("✅ All tests passed!")

# Run test
test_transpilation_scoring()
```

---

## FAQ

### Q1: Will this break my existing code?

**A**: No! The API is fully backward compatible. If you call `select_backend(circuit)` without any configuration, it will use sensible defaults (3 transpilation runs, mean aggregation).

---

### Q2: How much slower is transpilation scoring?

**A**: Research shows ~4.85ms per transpilation. For 20 backends × 3 runs = 60 transpilations ≈ 0.29 seconds. This is well under the 10-second performance target.

---

### Q3: What happens if transpilation fails for all backends?

**A**: A `ValueError` is raised with a clear message. You can catch this and handle it (e.g., simplify your circuit or use fewer qubits).

---

### Q4: Should I use 'mean', 'median', or 'minimum' aggregation?

**A**: 
- **Mean** (default): Balanced approach, good for most cases
- **Median**: Robust to outliers, use if transpilation is stochastic
- **Minimum**: Optimistic, assumes you'll get the best run

Research shows transpilation is **not stochastic by default**, so mean and minimum often give the same result.

---

### Q5: What are fractional gates?

**A**: Fractional gates are a backend configuration option in Qiskit. Research is ongoing to determine the exact parameter (deferred to Phase 1). The API supports three modes:
- `'both'` (default): Try both enabled and disabled, pick best
- `'enabled'`: Only use fractional gates
- `'disabled'`: Do not use fractional gates

---

### Q6: Can I see why a backend was excluded?

**A**: Yes, exclusions are logged at WARNING level:

```python
import logging

logging.basicConfig(level=logging.WARNING)
selector = BackendSelector(service)
ranked = selector.rank_backends(circuit)

# Check logs for exclusion reasons:
# WARNING: Backend ibm_lagos excluded: all 3 transpilations failed.
#          Last error: CircuitTooWideForTarget: exceeds backend qubits
```

---

## Next Steps

1. **Try the examples** in your own environment
2. **Experiment with configurations** to find what works best for your circuits
3. **Monitor performance** to ensure < 10s execution time
4. **Review transpilation details** to understand backend selection
5. **Report issues** on GitHub if you encounter problems

---

## Additional Resources

- **API Reference**: See `contracts/scoring_api.md` for detailed API specifications
- **Data Models**: See `data-model.md` for entity definitions
- **Research Findings**: See `research.md` for technical validation
- **Feature Spec**: See `spec.md` for requirements and user stories

---

## Phase 1 Sign-off

**Quickstart Status**: ✅ **COMPLETE**  
**Ready for Phase 2**: Pending agent context update  
**Blockers**: None

**Next Deliverable**: Update agent context with new data models and API contracts.
