# API Reference

Complete API documentation for the Enhanced Quantum Backend Selector.

## Overview

The library provides three main public classes:

- `BackendSelector` - Main API for backend selection
- `BackendRecommendation` - Selection results
- `BackendMetrics` - Backend specifications

## Quick Reference

### BackendSelector

Main class for selecting quantum backends.

```python
from enhanced_quantum_backend_selector import BackendSelector

selector = BackendSelector(backends: List[BackendV2])
```

**Methods:**

- `select_backend()` - Select the best backend for a circuit
- `rank_backends()` - Get ranked list of all backends

### BackendRecommendation

Result object containing backend selection details.

```python
@dataclass
class BackendRecommendation:
    backend: BackendV2          # The recommended backend
    score_data: CircuitScore    # Scoring results with negative error sum
    metrics: BackendMetrics     # Backend specifications
    rank: int                   # Position in rankings (1=best)
```

### CircuitScore

Scoring results for a backend.

```python
@dataclass
class CircuitScore:
    backend: str                # Backend name
    compatible: bool            # Whether backend can run the circuit
    reasons: list[str]          # Human-readable scoring explanations
    score: float                # Negative error sum (higher/less negative is better)
```

**Score Interpretation:**
- Score is the negative sum of all errors: `score = -total_error`
- Higher scores are better (less negative = lower error)
- Example: `-0.01` is better than `-0.05`
- Calculated from transpiled circuit with 3-run averaging

## Type Hierarchy

```
BackendSelector
├── __init__(backends: List[BackendV2])
├── select_backend() → BackendRecommendation
└── rank_backends() → List[BackendRecommendation]

BackendRecommendation
├── backend: BackendV2
├── score_data: CircuitScore
│   ├── backend: str
│   ├── compatible: bool
│   ├── reasons: List[str]
│   └── score: float (negative error sum, higher is better)
├── metrics: BackendMetrics
└── rank: int
```

**Note on Scoring:** The current implementation uses pure transpilation-based scoring where the score is calculated as the negative sum of all error rates from the transpiled circuit.

## Module Structure

```
enhanced_quantum_backend_selector/
├── __init__.py                    # Public API exports
├── backend_selector.py            # BackendSelector class
├── backend_analyzer.py            # Internal: Backend analysis
├── circuit_scorer.py              # Internal: Circuit scoring
└── models.py                      # Data models
```

## Public API

All public classes and functions are exported from the top-level module:

```python
from enhanced_quantum_backend_selector import (
    BackendSelector,
    BackendRecommendation,
    BackendMetrics,
    CircuitScore,
)
```

## Internal APIs

Internal modules in `exploration/` are not part of the public API and may change without notice. Use only the exported classes from the main module.

## Type Annotations

All public APIs have complete type annotations compatible with mypy strict mode:

```python
def select_backend(
    self,
    circuit: QuantumCircuit,
    top_n: int | None = None,
    require_compatible: bool = True,
    min_score: float | None = None,
) -> BackendRecommendation:
    ...
```

## See Also

- [User Guide](user-guide.md) - Usage examples and best practices
- [Architecture](architecture.md) - System design and implementation
- [Examples](examples.md) - Real-world usage scenarios
