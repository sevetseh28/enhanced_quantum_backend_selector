# API Reference

Complete API documentation for the Enhanced Quantum Backend Selector.

## Quick Reference

```python
from enhanced_quantum_backend_selector import (
    BackendSelector,
    BackendRecommendation,
    CircuitScore,
)
```

## BackendSelector

Main class for selecting quantum backends.

### Constructor

```python
BackendSelector(
    backends: List[BackendV2],
    transpilation_runs: int = 3
)
```

**Parameters:**

- `backends`: List of BackendV2 instances
- `transpilation_runs`: Number of transpilation runs for averaging (default: 3)

### Methods

#### select_backend

```python
def select_backend(
    self,
    circuit: QuantumCircuit,
    top_n: int | None = None,
    require_compatible: bool = True,
    min_score: float | None = None,
) -> BackendRecommendation
```

Select the best backend for a circuit.

**Parameters:**

- `circuit`: The quantum circuit to execute
- `top_n`: Consider only top N backends (optional)
- `require_compatible`: Only consider compatible backends (default: True)
- `min_score`: Minimum acceptable score (optional)

**Returns:** `BackendRecommendation`

**Raises:** `ValueError` if no suitable backend found

#### rank_backends

```python
def rank_backends(
    self,
    circuit: QuantumCircuit,
    top_n: int | None = None,
) -> List[BackendRecommendation]
```

Get ranked list of all backends.

**Parameters:**

- `circuit`: The quantum circuit to execute
- `top_n`: Return only top N backends (optional)

**Returns:** List of `BackendRecommendation` sorted by score

## BackendRecommendation

Result object containing backend selection details.

```python
@dataclass
class BackendRecommendation:
    backend: BackendV2          # The recommended backend
    score_data: CircuitScore    # Scoring results
    rank: int                   # Position in rankings (1=best)
```

## CircuitScore

Scoring results for a backend.

```python
@dataclass
class CircuitScore:
    backend: str                # Backend name
    compatible: bool            # Whether backend can run the circuit
    reasons: list[str]          # Human-readable explanations
    score: float                # Negative error sum (higher is better)
```

**Score interpretation:**

- Score = negative sum of all errors
- Higher scores are better (less negative = lower error)
- Example: `-0.01` (1% error) is better than `-0.05` (5% error)

## Type Hierarchy

```
BackendSelector
├── select_backend() → BackendRecommendation
└── rank_backends() → List[BackendRecommendation]

BackendRecommendation
├── backend: BackendV2
├── score_data: CircuitScore
└── rank: int

CircuitScore
├── backend: str
├── compatible: bool
├── reasons: List[str]
└── score: float
```

## Module Structure

```
enhanced_quantum_backend_selector/
├── __init__.py              # Public API exports
├── backend_selector.py      # BackendSelector class
├── backend_analyzer.py      # Internal: Backend analysis
├── circuit_scorer.py        # Internal: Circuit scoring
└── models.py                # Data models
```

## Example

```python
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from enhanced_quantum_backend_selector import BackendSelector

backends = [GenericBackendV2(num_qubits=5, seed=42)]
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

selector = BackendSelector(backends)
rec = selector.select_backend(qc)

print(f"Backend: {rec.backend.name}")
print(f"Score: {rec.score_data.score:.3f}")
print(f"Rank: #{rec.rank}")
```

## See Also

- [User Guide](user-guide.md) - Usage examples
- [Architecture](architecture.md) - System design
- [Examples](examples.md) - Real-world scenarios
