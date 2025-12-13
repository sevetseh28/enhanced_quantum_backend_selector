# Architecture

This document describes the design and implementation of the Enhanced Quantum Backend Selector.

## Overview

The library implements an intelligent backend selection system using **transpilation-based error estimation**. Rather than using generic backend metrics, it transpiles circuits to each backend and calculates the actual expected error rates based on the specific qubits and gates that will be used.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Application                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BackendSelector                           │
│  - Public API                                                │
│  - Input validation                                          │
│  - Result ranking                                            │
└────────┬───────────────────────────────┬────────────────────┘
         │                               │
         ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│  BackendAnalyzer     │      │   CircuitScorer      │
│  - Metrics extraction│      │   - Quality scoring  │
│  - Caching (1h TTL)  │      │   - Weight application
│  - Parallel queries  │      │   - Normalization    │
└──────────────────────┘      └──────────────────────┘
         │                               │
         ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Qiskit BackendV2 Interface                  │
│  - Backend properties                                        │
│  - Calibration data                                          │
│  - Queue information                                         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. BackendSelector

**Responsibility**: Public API and orchestration

**Key Features**:
- Validates input circuits and parameters
- Orchestrates parallel backend analysis
- Ranks backends by composite scores
- Returns strongly-typed recommendations

**Design Decisions**:
- Immutable after construction (backends list is frozen)
- Thread-safe for parallel scoring
- Caches backend metrics to minimize API calls

### 2. BackendAnalyzer

**Responsibility**: Extract and analyze backend metrics

**Metrics Collected**:
- Gate error rates (1Q, 2Q, readout)
- Coupling map topology
- Coherence times (T1, T2)
- Queue depth and operational status

**Caching Strategy**:
- 1-hour TTL on backend metrics
- Per-backend cache entries
- Timestamp-based invalidation
- Thread-safe cache access

### 3. CircuitScorer

**Responsibility**: Score backends using transpilation-based error estimation

**Scoring Method**:

1. **Transpile circuit** to backend with optimization level 2
2. **Identify used qubits** from transpiled circuit
3. **Sum all error sources** for those qubits:
   - Single-qubit gate errors
   - Two-qubit gate errors (for all gate types)
   - Readout errors
4. **Return negative error sum**: `score = -total_error`

**Multiple Runs**:
- Each backend is scored 3 times with independent transpilations
- Scores are averaged to account for layout variation
- Provides more stable and representative scoring

**Score Formula**:
```python
# For each transpilation run:
total_error = sum([
    single_qubit_errors,    # For all used qubits
    two_qubit_errors,       # For all used qubit pairs
    readout_errors,         # For all used qubits
])

score = -total_error

# Final score is average over 3 runs:
final_score = mean([score_run1, score_run2, score_run3])
```

**Advantages**:
- **Realistic**: Based on actual transpiled circuit, not generic metrics
- **Accurate**: Uses the specific qubits and gates that will execute
- **Comprehensive**: Includes all error sources in one metric
- **Stable**: Averaging reduces variation from layout randomness

### 4. Data Models

**BackendRecommendation**:
```python
@dataclass
class BackendRecommendation:
    backend: BackendV2           # The recommended backend
    score_data: CircuitScore     # Scoring results
    metrics: BackendMetrics      # Backend specifications
    rank: int                    # Position in rankings (1=best)
```

**CircuitScore**:
```python
@dataclass
class CircuitScore:
    backend: str                 # Backend name
    compatible: bool             # Circuit compatibility
    reasons: list[str]           # Human-readable explanations
    score: float                 # Negative error sum (higher is better)
```

**Note**: Current implementation uses pure transpilation-based scoring (negative error sum). The transpilation-based approach directly measures circuit quality on each backend by calculating actual expected errors.

## Data Flow

### Backend Selection Flow

```
1. User calls select_backend(circuit, weights)
   │
   ▼
2. BackendSelector validates inputs
   │
   ▼
3. Parallel scoring (ThreadPoolExecutor):
   ├─▶ Backend 1: Analyze + Score ──┐
   ├─▶ Backend 2: Analyze + Score ──┤
   ├─▶ Backend 3: Analyze + Score ──┼─▶ Collect results
   └─▶ Backend N: Analyze + Score ──┘
   │
   ▼
4. Sort by composite score (descending)
   │
   ▼
5. Filter by compatibility and min_score
   │
   ▼
6. Assign ranks (1 = best)
   │
   ▼
7. Return BackendRecommendation
```

### Scoring Flow

```
For each backend:
   │
   ▼
1. Check cache for metrics
   │
   ├─▶ Cache hit: Use cached data
   │
   └─▶ Cache miss:
       ├─▶ Query BackendV2 API
       ├─▶ Extract properties
       ├─▶ Calculate metrics
       └─▶ Store in cache (1h TTL)
   │
   ▼
2. Run 3 transpilation passes:
   │
   For each run (i = 1, 2, 3):
   ├─▶ Transpile circuit to backend (optimization_level=2)
   ├─▶ Identify used qubits in transpiled circuit
   ├─▶ Sum error rates:
   │   ├─▶ Single-qubit gate errors (all used qubits)
   │   ├─▶ Two-qubit gate errors (all used qubit pairs)
   │   └─▶ Readout errors (all used qubits)
   └─▶ score_i = -total_error
   │
   ▼
3. Average the 3 scores:
   final_score = mean([score_1, score_2, score_3])
   │
   ▼
4. Return CircuitScore object:
   ├─▶ backend name
   ├─▶ compatibility flag
   ├─▶ final_score (negative error sum)
   └─▶ human-readable reasons
```

## Performance Optimizations

### 1. Parallel Backend Analysis

- Uses `ThreadPoolExecutor` with max 10 workers
- Analyzes all backends concurrently
- Reduces latency for large backend pools

### 2. Metric Caching

- Caches backend properties for 1 hour
- Avoids repeated API calls
- Reduces load on quantum providers
- Per-selector instance (not global)

### 3. Lazy Evaluation

- Only scores backends when needed
- Supports `top_n` to limit results
- Early termination for single selection

## Design Patterns

### 1. Transpilation-Based Scoring

The current implementation uses direct transpilation to measure circuit quality:

```python
# Circuit is transpiled to each backend with optimization_level=2
# Score is calculated as negative sum of all error rates
score = -total_error  # Higher (less negative) is better
```

**Rationale**: Transpilation reveals the actual qubits and gates that will be used, providing more accurate quality estimates than generic backend metrics.

### 2. Multiple Run Averaging

Each backend is scored 3 times with independent transpilations:

```python
scores = [transpile_and_score() for _ in range(3)]
final_score = mean(scores)
```

**Rationale**: Transpilation can produce different layouts. Averaging provides stability and reduces sensitivity to single unlucky transpilations.

### 2. Builder Pattern

BackendRecommendation built incrementally:

```python
# Internal scoring process
score_data = scorer.score(circuit, backend)
metrics = analyzer.get_metrics(backend)
recommendation = BackendRecommendation(backend, score_data, metrics, rank)
```

### 3. Dependency Injection

BackendSelector receives backends at construction:

```python
# Testable with mock backends
selector = BackendSelector(backends)
```

## Error Handling

### Validation Errors

```python
# Raised immediately
if not backends:
    raise ValueError("No backends provided")

if circuit.num_qubits < 1:
    raise ValueError("Circuit must have at least 1 qubit")
```

### Selection Failures

```python
# Raised when no backends meet criteria
if not compatible_backends:
    raise ValueError("No compatible backends found")

if not meets_min_score:
    raise ValueError("No backends meet minimum score")
```

### Graceful Degradation

```python
# Missing calibration data
if not backend.properties:
    # Use conservative estimates
    fidelity_score = 0.5
```

## Testing Strategy

### 1. Unit Tests

- Test individual components in isolation
- Mock Qiskit backends with `GenericBackendV2`
- Verify scoring algorithms mathematically

### 2. Integration Tests

- Test full selection workflow
- Use Aer simulators and fake backends
- Verify caching and parallel execution

### 3. Validation Tests

- Compare against `least_busy()` baseline
- Use canonical quantum circuits (GHZ, QFT, VQE)
- Verify scoring improves on simple strategies

## Security Considerations

### 1. Input Validation

All public methods validate inputs:

```python
# Check parameter ranges
if min_score < 0 or min_score > 1:
    raise ValueError("min_score must be in [0, 1]")

# Check weight values
if any(w < 0 for w in [fidelity_w, connectivity_w, coherence_w, queue_w]):
    raise ValueError("Weights must be non-negative")
```

### 2. Safe Concurrency

- Thread-safe cache implementation
- No shared mutable state between threads
- Immutable data models

### 3. Resource Limits

- Maximum 10 parallel workers (prevents resource exhaustion)
- 1-hour cache TTL (prevents stale data)
- No unbounded collections

## Extensibility

### Improving Scoring Accuracy

The current transpilation-based scoring can be enhanced:

1. **Add more transpilation runs**: Increase from 3 to 5+ runs for better averaging
   ```python
   for run_num in range(5):  # Currently 3
       transpiled = transpile(circuit, backend=backend, optimization_level=2)
   ```

2. **Add error mitigation analysis**: Factor in error mitigation capabilities
   ```python
   if backend.supports_error_mitigation:
       score_adjustment = calculate_mitigation_benefit()
   ```

3. **Consider additional metrics**: Add queue time, gate set richness, etc.
   ```python
   queue_penalty = calculate_queue_impact(backend.status().pending_jobs)
   adjusted_score = base_score - queue_penalty
   ```

### Supporting New Backend Types

The library works with any `BackendV2` implementation:

```python
# Automatically supports new providers
from new_provider import NewBackendV2

backends = [NewBackendV2(...)]
selector = BackendSelector(backends)  # Just works
```

## Future Enhancements

### Potential Improvements

1. **Machine Learning**:
   - Train models on historical job performance
   - Predict circuit success probability

2. **Dynamic Weights**:
   - Auto-adjust weights based on circuit characteristics
   - Learn from user preferences

3. **Multi-Circuit Optimization**:
   - Batch backend selection
   - Load balancing across backends

4. **Advanced Caching**:
   - Persistent cache across sessions
   - Shared cache for multiple selectors

5. **Cost Analysis**:
   - Include pricing in selection criteria
   - Budget-constrained optimization

## See Also

- [API Reference](api-reference.md) - Complete API documentation
- [User Guide](user-guide.md) - Usage patterns and best practices
- [Contributing](contributing.md) - Development guidelines
