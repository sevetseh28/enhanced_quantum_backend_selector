# Architecture

Design and implementation of the Enhanced Quantum Backend Selector.

## Overview

The library implements intelligent backend selection using **transpilation-based error estimation**. Rather than using generic backend metrics, it transpiles circuits to each backend and calculates the actual expected error rates.

## System Architecture

```
┌────────────────────────────────────────────────┐
│              User Application                   │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│              BackendSelector                    │
│  - Public API                                   │
│  - Input validation                             │
│  - Parallel scoring                             │
│  - Result ranking                               │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│              BackendAnalyzer                    │
│  - Per-instance caching                         │
│  - Delegates to CircuitScorer                   │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│              CircuitScorer                      │
│  - Error calculation                            │
│  - Gate error summation                         │
│  - Readout error handling                       │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│          Qiskit BackendV2 Interface             │
└────────────────────────────────────────────────┘
```

## Core Components

### BackendSelector

**Responsibility:** Public API and orchestration

- Validates inputs
- Transpiles circuits to each backend
- Orchestrates parallel backend scoring
- Ranks backends by scores
- Returns strongly-typed recommendations

### BackendAnalyzer

**Responsibility:** Backend analysis wrapper

- Wraps a single backend
- Creates CircuitScorer for scoring
- Cached per-selector instance

### CircuitScorer

**Responsibility:** Score circuits using error analysis

**Scoring method:**

1. Sum error rates for each gate operation in transpiled circuit
2. Add readout error for each used qubit
3. Return negative error sum: `score = -total_error`

**Note:** Transpilation happens in `BackendSelector`, which then passes the transpiled circuit to the scorer.

**Multiple runs:** BackendSelector averages over 3 transpilation runs for stability.

```python
# Score formula (in CircuitScorer)
total_error = sum(gate.error_rate for gate in transpiled_circuit)
total_error += sum(qubit.readout_error for qubit in used_qubits)
score = -total_error

# Averaging (in BackendSelector)
final_score = mean([score_run1, score_run2, score_run3])
```

## Data Models

### BackendRecommendation

```python
@dataclass
class BackendRecommendation:
    backend: BackendV2
    score_data: CircuitScore
    rank: int
```

### CircuitScore

```python
@dataclass
class CircuitScore:
    backend: str
    compatible: bool
    reasons: list[str]
    score: float  # Negative error sum
```

## Data Flow

```
1. User calls select_backend(circuit)
2. BackendSelector validates inputs
3. Parallel scoring (ThreadPoolExecutor, 10 workers):
   └─▶ Each backend: Transpile + Calculate error
4. Sort by score (descending)
5. Filter by compatibility and min_score
6. Assign ranks (1 = best)
7. Return BackendRecommendation
```

## Performance

### Parallel Analysis

- Uses ThreadPoolExecutor with max 10 workers
- Analyzes all backends concurrently

### Caching

- Backend analyzers cached per-selector instance
- Use `selector.clear_cache()` to force fresh analysis

### Configurable Accuracy

- Default: 3 transpilation runs
- Configurable: 1 (fast) to 5+ (accurate)

## Design Decisions

### Why Transpilation-Based?

Transpiling reveals:

- Which specific qubits will be used
- Exact gate decompositions needed
- Real error rates for actual execution

This is more accurate than generic backend metrics.

### Why Multiple Runs?

Transpilation can produce different layouts. Averaging provides:

- More stable scoring
- Reduced sensitivity to single unlucky transpilations

### Provider Agnostic

Works with any BackendV2 implementation:

```python
from any_provider import AnyBackendV2
selector = BackendSelector([AnyBackendV2(...)])
```

## Error Handling

```python
# Validation errors
if not backends:
    raise ValueError("No backends provided")

# Selection failures
if not compatible_backends:
    raise ValueError("No compatible backends found")
```

## Testing Strategy

- **Unit tests:** Individual components with mock backends
- **Integration tests:** Full workflow with fake backends
- **Validation tests:** Compare against baseline methods

## See Also

- [API Reference](api-reference.md) - Complete API documentation
- [User Guide](user-guide.md) - Usage patterns
- [Contributing](contributing.md) - Development guidelines
