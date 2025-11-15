# Architecture

This document describes the design and implementation of the Enhanced Quantum Backend Selector.

## Overview

The library implements a multi-criteria decision system for quantum backend selection, using a weighted scoring approach across four key quality factors.

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

**Responsibility**: Score backends against circuit requirements

**Scoring Components**:

1. **Gate Fidelity Score** (0-1):
   - Average of 1-qubit, 2-qubit, and readout fidelities
   - Normalized by error rates: `1 - error_rate`

2. **Connectivity Score** (0-1):
   - Based on coupling map size
   - Linear normalization: `edges / max_edges`

3. **Coherence Score** (0-1):
   - T1 and T2 times relative to circuit depth
   - Formula: `exp(-circuit_time / coherence_time)`

4. **Queue Score** (0-1):
   - Inverse of pending jobs
   - Formula: `1 / (1 + pending_jobs)`

**Composite Score**:
```python
total_score = (
    fidelity_score * fidelity_weight +
    connectivity_score * connectivity_weight +
    coherence_score * coherence_weight +
    queue_score * queue_weight
)
```

### 4. Data Models

**BackendRecommendation**:
```python
@dataclass
class BackendRecommendation:
    backend: BackendV2           # The recommended backend
    score_data: CircuitScore     # Detailed scoring info
    metrics: BackendMetrics      # Backend specifications
    rank: int                    # Position in rankings
```

**ScoringWeights**:
```python
@dataclass
class ScoringWeights:
    gate_fidelity_weight: float = 1.5
    connectivity_weight: float = 1.0
    coherence_weight: float = 0.8
    queue_weight: float = 0.4
```

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
2. Calculate component scores:
   ├─▶ Gate fidelity (from error rates)
   ├─▶ Connectivity (from coupling map)
   ├─▶ Coherence (from T1/T2 times)
   └─▶ Queue time (from pending jobs)
   │
   ▼
3. Apply weights and sum
   │
   ▼
4. Return CircuitScore object
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

### 1. Strategy Pattern

ScoringWeights allows runtime configuration of scoring strategy:

```python
# Different strategies for different use cases
quality_first = ScoringWeights(2.0, 1.5, 1.5, 0.2)
speed_first = ScoringWeights(0.5, 0.8, 0.5, 3.0)
```

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

### Adding New Scoring Factors

1. Add weight to `ScoringWeights`:
   ```python
   new_factor_weight: float = 1.0
   ```

2. Calculate score in `CircuitScorer`:
   ```python
   new_score = calculate_new_factor(backend, circuit)
   ```

3. Include in composite score:
   ```python
   total += new_score * weights.new_factor_weight
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
