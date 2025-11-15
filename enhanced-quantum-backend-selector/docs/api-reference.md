# API Reference

Complete API documentation for the Enhanced Quantum Backend Selector.

## Overview

The library provides three main public classes:

- [`BackendSelector`](api/backend-selector.md) - Main API for backend selection
- [`ScoringWeights`](api/scoring-weights.md) - Configuration for scoring priorities
- [`BackendRecommendation`](api/data-models.md#backendrecommendation) - Selection results

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

[Full documentation →](api/backend-selector.md)

### ScoringWeights

Configuration for multi-criteria scoring.

```python
from enhanced_quantum_backend_selector import ScoringWeights

weights = ScoringWeights(
    gate_fidelity_weight: float = 1.5,
    connectivity_weight: float = 1.0,
    coherence_weight: float = 0.8,
    queue_weight: float = 0.4,
)
```

[Full documentation →](api/scoring-weights.md)

### BackendRecommendation

Result object containing backend selection details.

```python
@dataclass
class BackendRecommendation:
    backend: BackendV2
    score_data: CircuitScore
    metrics: BackendMetrics
    rank: int
```

[Full documentation →](api/data-models.md)

## Type Hierarchy

```
BackendSelector
├── __init__(backends: List[BackendV2])
├── select_backend() → BackendRecommendation
└── rank_backends() → List[BackendRecommendation]

BackendRecommendation
├── backend: BackendV2
├── score_data: CircuitScore
├── metrics: BackendMetrics
└── rank: int

ScoringWeights
├── gate_fidelity_weight: float
├── connectivity_weight: float
├── coherence_weight: float
└── queue_weight: float
```

## Module Structure

```
enhanced_quantum_backend_selector/
├── __init__.py                    # Public API exports
├── backend_selector.py            # BackendSelector class
├── scoring_weights.py             # ScoringWeights class
├── models.py                      # Data models
└── exploration/
    ├── backend_analyzer.py        # Internal: Backend analysis
    ├── circuit_scorer.py          # Internal: Circuit scoring
    └── ...                        # Other internal modules
```

## Public API

All public classes and functions are exported from the top-level module:

```python
from enhanced_quantum_backend_selector import (
    BackendSelector,
    BackendRecommendation,
    ScoringWeights,
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
    weights: ScoringWeights | None = None,
    top_n: int | None = None,
    require_compatible: bool = True,
    min_score: float = 0.0,
) -> BackendRecommendation:
    ...
```

## Detailed Documentation

- [BackendSelector API](api/backend-selector.md)
- [ScoringWeights API](api/scoring-weights.md)
- [Data Models API](api/data-models.md)

## See Also

- [User Guide](user-guide.md) - Usage examples and best practices
- [Architecture](architecture.md) - System design and implementation
- [Examples](examples.md) - Real-world usage scenarios
