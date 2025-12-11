# API Contract: Transpiled Circuit Scoring

**Feature**: `002-transpiled-error-scoring`  
**Date**: December 11, 2025  
**Status**: Phase 1 Design

## Overview

This document specifies the API contracts for transpiled circuit error-based scoring. It covers:
1. Modified public API methods (backward compatible)
2. New internal helper functions
3. Error handling contracts
4. Caching behavior

---

## Public API Changes

### 1. `BackendSelector.select_backend()`

**Signature** (Modified):

```python
def select_backend(
    self,
    circuit: QuantumCircuit,
    weights: Optional[ScoringWeights] = None,
    config: Optional[ScoringConfiguration] = None  # NEW PARAMETER
) -> BackendRecommendation:
    """
    Select the best backend for the given quantum circuit.
    
    Args:
        circuit: Quantum circuit to execute
        weights: Custom scoring weights (backward compatible, deprecated)
        config: Transpilation scoring configuration (NEW)
    
    Returns:
        BackendRecommendation with highest score
    
    Raises:
        ValueError: If all backends fail transpilation (FR-013)
        TypeError: If circuit is not QuantumCircuit
        ValueError: If config and weights both provided (use config.weights)
    
    Backward Compatibility:
        - weights parameter still supported (deprecated)
        - If config is None, uses ScoringConfiguration() defaults
        - If weights provided without config, creates config with weights
    """
```

**Changes**:
- **New Parameter**: `config` (Optional[ScoringConfiguration])
- **Deprecation**: `weights` parameter deprecated in favor of `config.weights`
- **Behavior**: If `config` is None, defaults to standard transpilation scoring with mean aggregation

**Example Usage**:

```python
# Backward compatible (no changes needed)
selector = BackendSelector(service)
best = selector.select_backend(circuit)

# With configuration
config = ScoringConfiguration(
    transpilation_runs=5,
    aggregation_method='median'
)
best = selector.select_backend(circuit, config=config)

# Deprecated but still works
weights = ScoringWeights(error_rate=1.0, gate_fidelity=0.8)
best = selector.select_backend(circuit, weights=weights)
```

---

### 2. `BackendSelector.rank_backends()`

**Signature** (Modified):

```python
def rank_backends(
    self,
    circuit: QuantumCircuit,
    weights: Optional[ScoringWeights] = None,
    config: Optional[ScoringConfiguration] = None  # NEW PARAMETER
) -> List[BackendRecommendation]:
    """
    Rank all backends for the given quantum circuit.
    
    Args:
        circuit: Quantum circuit to execute
        weights: Custom scoring weights (backward compatible, deprecated)
        config: Transpilation scoring configuration (NEW)
    
    Returns:
        List of BackendRecommendation sorted by score (highest first)
        Excludes backends that fail transpilation (FR-012)
    
    Raises:
        ValueError: If all backends fail transpilation (FR-013)
        TypeError: If circuit is not QuantumCircuit
        ValueError: If config and weights both provided
    
    Backward Compatibility:
        - weights parameter still supported (deprecated)
        - If config is None, uses ScoringConfiguration() defaults
        - If weights provided without config, creates config with weights
    
    Behavior:
        - Backends that fail all transpilations are excluded
        - Each excluded backend logged with failure reason (FR-012)
        - If fractional_gates_mode='both', transpiles 2x per run
    """
```

**Changes**:
- **New Parameter**: `config` (Optional[ScoringConfiguration])
- **Exclusion Logic**: Backends failing all transpilations are filtered out
- **Return Value**: List may be shorter than input backends if failures occur

**Example Usage**:

```python
# Backward compatible
selector = BackendSelector(service)
ranked = selector.rank_backends(circuit)

# With custom config
config = ScoringConfiguration(
    transpilation_runs=3,
    aggregation_method='minimum',
    fractional_gates_mode='both'
)
ranked = selector.rank_backends(circuit, config=config)

# Check for exclusions
for rec in ranked:
    if rec.transpilation_details:
        print(f"{rec.backend.name}: {rec.transpilation_details.final_score:.6f}")
```

---

## Internal Helper Functions

### 3. `BackendSelector._transpile_circuit()`

**Signature** (New):

```python
def _transpile_circuit(
    self,
    circuit: QuantumCircuit,
    backend: BackendV2,
    fractional_gates: bool,
    optimization_level: int
) -> TranspilationRun:
    """
    Transpile circuit for a specific backend configuration.
    
    Args:
        circuit: Source quantum circuit
        backend: Target backend
        fractional_gates: Enable fractional gates (if supported)
        optimization_level: Qiskit optimization level (0-3)
    
    Returns:
        TranspilationRun with success status and error sum
    
    Side Effects:
        - Logs warning if transpilation fails (FR-012)
        - Logs warning if instruction missing error data (FR-008)
    
    Error Handling:
        - Catches TranspilerError → TranspilationRun(success=False)
        - Catches Exception → TranspilationRun(success=False)
        - Never raises exceptions to caller
    """
```

**Implementation Notes**:
- Uses `transpile(circuit, backend=backend, optimization_level=optimization_level)`
- Fractional gates parameter research deferred (see research.md)
- All exceptions caught and converted to failed TranspilationRun

**Example**:

```python
run = self._transpile_circuit(
    circuit=user_circuit,
    backend=fake_manila,
    fractional_gates=False,
    optimization_level=3
)

if run.success:
    print(f"Transpiled to {run.num_instructions} instructions")
    print(f"Total error: {run.error_sum:.6f}")
else:
    print(f"Failed: {run.failure_reason}")
```

---

### 4. `BackendSelector._calculate_error_sum()`

**Signature** (New):

```python
def _calculate_error_sum(
    self,
    transpiled_circuit: QuantumCircuit,
    backend: BackendV2
) -> Tuple[float, int]:
    """
    Calculate sum of error rates for all instructions in transpiled circuit.
    
    Args:
        transpiled_circuit: Circuit with native gates only
        backend: Backend with calibration data
    
    Returns:
        Tuple of (error_sum, missing_count)
        - error_sum: Sum of all instruction error rates
        - missing_count: Count of instructions without error data
    
    Implementation:
        - Uses backend.target[operation_name][qubits].error
        - Skips instructions with missing error data (FR-008)
        - Logs warning for each missing error (FR-008)
        - Never raises exceptions
    
    Edge Cases:
        - If all instructions missing errors: returns (0.0, instruction_count)
        - Global operations (no qubits): check target[op_name][()]
        - Unsupported operations: counted as missing
    """
```

**Example**:

```python
error_sum, missing = self._calculate_error_sum(
    transpiled_circuit=transpiled_qc,
    backend=fake_manila
)

if missing > 0:
    logger.warning(
        f"Backend {backend.name}: {missing}/{transpiled_qc.size()} "
        f"instructions missing error data"
    )
```

---

### 5. `BackendSelector._aggregate_scores()`

**Signature** (New):

```python
def _aggregate_scores(
    self,
    runs: List[TranspilationRun],
    method: str
) -> Optional[AggregatedScore]:
    """
    Aggregate multiple transpilation runs into single score.
    
    Args:
        runs: List of transpilation attempts
        method: Aggregation method ('mean', 'median', 'minimum')
    
    Returns:
        AggregatedScore if any runs succeeded, None if all failed
    
    Implementation:
        - Filters out failed runs before aggregation
        - Uses statistics.mean/median or min() built-in
        - Calculates variance and std_dev (FR-011)
        - Returns None if all runs failed (FR-012)
    
    Validation:
        - method must be 'mean', 'median', or 'minimum'
        - Raises ValueError if invalid method
    """
```

**Example**:

```python
runs = [
    self._transpile_circuit(circuit, backend, False, 3),
    self._transpile_circuit(circuit, backend, False, 3),
    self._transpile_circuit(circuit, backend, False, 3),
]

agg_score = self._aggregate_scores(runs, method='mean')

if agg_score is None:
    logger.warning(f"Backend {backend.name}: All transpilations failed")
    return None  # Exclude backend
```

---

### 6. `BackendSelector._score_backend_with_transpilation()`

**Signature** (New):

```python
def _score_backend_with_transpilation(
    self,
    circuit: QuantumCircuit,
    backend: BackendV2,
    config: ScoringConfiguration
) -> Optional[BackendRecommendation]:
    """
    Score a backend using transpiled circuit error-based method.
    
    Args:
        circuit: Source quantum circuit
        backend: Backend to score
        config: Transpilation configuration
    
    Returns:
        BackendRecommendation if any transpilations succeeded
        None if all transpilations failed (backend excluded)
    
    Implementation Flow:
        1. Determine fractional_gates configurations to try
        2. For each configuration:
           - Transpile config.transpilation_runs times
           - Aggregate scores using config.aggregation_method
        3. If fractional_gates_mode='both':
           - Compare aggregated scores, pick best
        4. Create BackendRecommendation with transpilation_details
    
    Parallelization:
        - Uses ThreadPoolExecutor for parallel transpilations (FR-016)
        - Pools transpilations within backend (not across backends)
        - Max workers = min(config.transpilation_runs, cpu_count)
    
    Caching:
        - Backend calibration data cached with 1-hour TTL (FR-017)
        - Transpilation results NOT cached (circuits may differ)
    """
```

**Example**:

```python
config = ScoringConfiguration(
    transpilation_runs=5,
    aggregation_method='median',
    fractional_gates_mode='both'
)

recommendation = self._score_backend_with_transpilation(
    circuit=user_circuit,
    backend=fake_manila,
    config=config
)

if recommendation is None:
    print(f"{fake_manila.name} excluded (all transpilations failed)")
else:
    print(f"{fake_manila.name}: {recommendation.transpilation_details.final_score:.6f}")
```

---

## Error Handling Contracts

### Exception Types

| Exception | Thrown By | Condition | User-Facing? |
|-----------|-----------|-----------|--------------|
| `ValueError` | `select_backend()` | All backends fail transpilation | ✅ Yes |
| `ValueError` | `rank_backends()` | All backends fail transpilation | ✅ Yes |
| `ValueError` | `ScoringConfiguration.__post_init__` | Invalid parameter values | ✅ Yes |
| `TypeError` | `select_backend()` | circuit not QuantumCircuit | ✅ Yes |
| `TranspilerError` | `_transpile_circuit()` | Transpilation failure | ❌ No (caught internally) |
| `KeyError` | `_calculate_error_sum()` | Missing target operation | ❌ No (counted as missing) |

### Error Messages (User-Facing)

```python
# All backends failed
raise ValueError(
    f"All {len(backends)} backends failed transpilation for circuit. "
    f"Check circuit compatibility or reduce circuit depth."
)

# Invalid configuration
raise ValueError(
    f"transpilation_runs must be positive integer, got {value}"
)

# Type error
raise TypeError(
    f"circuit must be QuantumCircuit, got {type(circuit)}"
)
```

### Logging Contracts (Internal)

```python
# Backend excluded (FR-012)
logger.warning(
    f"Backend {backend.name} excluded: all {runs} transpilations failed. "
    f"Last error: {failure_reason}"
)

# Missing error data (FR-008)
logger.warning(
    f"Backend {backend.name}: instruction {instruction.operation.name} "
    f"on qubits {qubits} missing error rate data, skipping"
)

# Successful transpilation (debug level)
logger.debug(
    f"Backend {backend.name}: transpiled to {num_instructions} instructions, "
    f"error sum = {error_sum:.6f}"
)
```

---

## Caching Behavior

### Cached Data (FR-017)

| Data | Cache Key | TTL | Scope |
|------|-----------|-----|-------|
| Backend calibration data | `backend.name` | 1 hour | Instance |
| Target error rates | `backend.name` | 1 hour | Instance |

### NOT Cached

- Transpilation results (circuits may differ between calls)
- AggregatedScore objects (user config may change)
- TranspilationRun objects (tied to specific circuit)

### Cache Implementation

```python
from functools import lru_cache
from time import time

class BackendSelector:
    def __init__(self, service):
        self._service = service
        self._calibration_cache = {}
        self._cache_ttl = 3600  # 1 hour in seconds
    
    def _get_backend_calibration(self, backend: BackendV2) -> Target:
        """Get cached or fresh backend calibration data."""
        cache_key = backend.name
        now = time()
        
        if cache_key in self._calibration_cache:
            data, timestamp = self._calibration_cache[cache_key]
            if now - timestamp < self._cache_ttl:
                return data
        
        # Fetch fresh data
        target = backend.target
        self._calibration_cache[cache_key] = (target, now)
        return target
```

---

## Performance Contracts

### Time Budgets (SC-005, FR-018)

| Operation | Target | Measured (Research) | Status |
|-----------|--------|---------------------|--------|
| Single transpilation | < 10ms | 4.85ms avg | ✅ Pass |
| 3 runs per backend | < 30ms | 14.55ms | ✅ Pass |
| 20 backends × 3 runs | < 10s | ~0.29s | ✅ Pass |

### Parallelization (FR-016)

```python
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count

def _score_backend_with_transpilation(self, circuit, backend, config):
    """Parallelized transpilation within backend."""
    max_workers = min(config.transpilation_runs, cpu_count() or 4)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                self._transpile_circuit,
                circuit, backend, fractional_gates, config.optimization_level
            )
            for _ in range(config.transpilation_runs)
        ]
        runs = [f.result() for f in futures]
    
    return self._aggregate_scores(runs, config.aggregation_method)
```

---

## Backward Compatibility Matrix

| Usage Pattern | Before | After | Compatible? |
|---------------|--------|-------|-------------|
| `select_backend(circuit)` | ✅ Works | ✅ Works (defaults used) | ✅ Yes |
| `select_backend(circuit, weights)` | ✅ Works | ⚠️ Works (deprecated warning) | ✅ Yes |
| `rank_backends(circuit)` | ✅ Works | ✅ Works (defaults used) | ✅ Yes |
| Return type `BackendRecommendation` | ✅ Has fields | ✅ Has fields + optional new fields | ✅ Yes |
| `recommendation.score_data` | ✅ Works | ✅ Works (unchanged) | ✅ Yes |
| `recommendation.transpiration_details` | ❌ AttributeError | ✅ Optional[AggregatedScore] | ⚠️ New field |

**Breaking Change**: None  
**Deprecation**: `weights` parameter in favor of `config.weights`

---

## API Stability Guarantees

### Public API (Stable)
- `BackendSelector.select_backend()`
- `BackendSelector.rank_backends()`
- `BackendRecommendation` dataclass
- `ScoringConfiguration` dataclass
- `AggregatedScore` dataclass

### Internal API (Unstable)
- `_transpile_circuit()`
- `_calculate_error_sum()`
- `_aggregate_scores()`
- `_score_backend_with_transpilation()`
- `_get_backend_calibration()`

**Versioning**: Following constitution, internal methods may change without notice.

---

## Testing Contracts

### Unit Test Requirements

Each function must have tests for:

1. **Happy Path**: Standard inputs, expected outputs
2. **Edge Cases**: Empty lists, single-element lists, None values
3. **Error Handling**: Invalid inputs raise correct exceptions
4. **Validation**: `__post_init__` validates dataclass fields

### Integration Test Requirements

- End-to-end `select_backend()` with real Fake backends
- End-to-end `rank_backends()` with multiple backends
- Fractional gates mode 'both' creates 2x transpilations
- Backend exclusion when all transpilations fail
- Aggregation methods (mean/median/minimum) produce different rankings

### Performance Test Requirements

- 20 backends × 3 runs < 10 seconds (SC-005)
- Parallelization provides speedup over sequential
- Cache hit avoids redundant backend fetches

---

## Phase 1 Sign-off

**API Contracts Status**: ✅ **COMPLETE**  
**Ready for Phase 2**: Pending quickstart examples  
**Blockers**: None

**Next Deliverable**: `quickstart.md` with usage examples and migration guide.
