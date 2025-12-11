# Data Model: Transpiled Circuit Error-Based Scoring

**Feature**: `002-transpiled-error-scoring`  
**Date**: December 11, 2025  
**Status**: Phase 1 Design

## Overview

This document specifies the data models (entities) required for implementing transpiled circuit error-based scoring. All entities follow the constitution principle of strong typing and will be implemented as Python dataclasses in `models.py`.

---

## New Entities

### 1. TranspilationRun

Captures the result of a single transpilation attempt.

**Purpose**: Track individual transpilation outcomes to support multi-run aggregation and transparency (FR-011).

**Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| `circuit` | `QuantumCircuit` | The transpiled circuit (native gates) |
| `success` | `bool` | Whether transpilation succeeded |
| `error_sum` | `Optional[float]` | Sum of instruction error rates (None if failed) |
| `failure_reason` | `Optional[str]` | Error message if transpilation failed |
| `fractional_gates` | `bool` | Which fractional gates config was used |
| `num_instructions` | `int` | Count of instructions in transpiled circuit |
| `missing_error_count` | `int` | Count of instructions with missing error data |

**Python Implementation**:

```python
from dataclasses import dataclass
from typing import Optional
from qiskit.circuit import QuantumCircuit

@dataclass
class TranspilationRun:
    """Result of a single transpilation attempt."""
    
    circuit: Optional[QuantumCircuit]
    success: bool
    error_sum: Optional[float]
    failure_reason: Optional[str] = None
    fractional_gates: bool = False
    num_instructions: int = 0
    missing_error_count: int = 0
    
    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if self.success and self.error_sum is None:
            raise ValueError("Successful run must have error_sum")
        if not self.success and self.failure_reason is None:
            raise ValueError("Failed run must have failure_reason")
```

**Usage Example**:

```python
# Successful transpilation
run = TranspilationRun(
    circuit=transpiled_qc,
    success=True,
    error_sum=0.024703,
    fractional_gates=False,
    num_instructions=9,
    missing_error_count=0
)

# Failed transpilation
failed_run = TranspilationRun(
    circuit=None,
    success=False,
    error_sum=None,
    failure_reason="CircuitTooWideForTarget: exceeds backend qubits",
    fractional_gates=False
)
```

---

### 2. AggregatedScore

Contains the final score derived from multiple transpilation runs.

**Purpose**: Provide transparent scoring details including individual run results and statistical metadata (FR-011, SC-007).

**Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| `final_score` | `float` | Aggregated error sum (mean/median/minimum) |
| `individual_scores` | `List[float]` | Error sums from each successful run |
| `aggregation_method` | `str` | Method used: 'mean', 'median', or 'minimum' |
| `successful_runs` | `int` | Count of successful transpilations |
| `failed_runs` | `int` | Count of failed transpilations |
| `variance` | `Optional[float]` | Statistical variance of individual scores |
| `std_dev` | `Optional[float]` | Standard deviation of individual scores |

**Python Implementation**:

```python
from dataclasses import dataclass, field
from typing import List, Optional
from statistics import mean, median, stdev, variance as calc_variance

@dataclass
class AggregatedScore:
    """Score aggregated from multiple transpilation runs."""
    
    final_score: float
    individual_scores: List[float]
    aggregation_method: str
    successful_runs: int
    failed_runs: int
    variance: Optional[float] = None
    std_dev: Optional[float] = None
    
    def __post_init__(self) -> None:
        """Calculate statistics after initialization."""
        if len(self.individual_scores) != self.successful_runs:
            raise ValueError(
                f"individual_scores length ({len(self.individual_scores)}) "
                f"must match successful_runs ({self.successful_runs})"
            )
        
        # Calculate variance and std dev if multiple runs
        if self.successful_runs >= 2:
            self.variance = calc_variance(self.individual_scores)
            self.std_dev = stdev(self.individual_scores)
        
        # Validate aggregation method
        if self.aggregation_method not in ['mean', 'median', 'minimum']:
            raise ValueError(
                f"Invalid aggregation_method: {self.aggregation_method}"
            )
    
    @classmethod
    def from_runs(
        cls,
        runs: List['TranspilationRun'],
        method: str = 'mean'
    ) -> 'AggregatedScore':
        """Create AggregatedScore from TranspilationRun list."""
        successful = [r for r in runs if r.success]
        failed = [r for r in runs if not r.success]
        
        if not successful:
            raise ValueError("No successful transpilation runs to aggregate")
        
        scores = [r.error_sum for r in successful if r.error_sum is not None]
        
        if method == 'mean':
            final = mean(scores)
        elif method == 'median':
            final = median(scores)
        elif method == 'minimum':
            final = min(scores)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
        
        return cls(
            final_score=final,
            individual_scores=scores,
            aggregation_method=method,
            successful_runs=len(successful),
            failed_runs=len(failed)
        )
```

**Usage Example**:

```python
# Create from transpilation runs
agg_score = AggregatedScore.from_runs(
    runs=[run1, run2, run3],
    method='mean'
)

print(f"Final score: {agg_score.final_score:.6f}")
print(f"Variance: {agg_score.variance:.6f}")
print(f"Successful: {agg_score.successful_runs}/{agg_score.successful_runs + agg_score.failed_runs}")
```

---

### 3. ScoringConfiguration

Encapsulates user-configurable parameters for transpiled circuit scoring.

**Purpose**: Provide clean API for user customization (FR-005, FR-006, FR-009, FR-010).

**Attributes**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `transpilation_runs` | `int` | `3` | Number of transpilation attempts per backend |
| `aggregation_method` | `str` | `'mean'` | Statistical measure: 'mean', 'median', or 'minimum' |
| `fractional_gates_mode` | `str` | `'both'` | Evaluation mode: 'both', 'enabled', 'disabled' |
| `optimization_level` | `int` | `3` | Qiskit transpiler optimization level (0-3) |
| `weights` | `Optional[ScoringWeights]` | `None` | Existing scoring weights (backward compatible) |

**Python Implementation**:

```python
from dataclasses import dataclass
from typing import Optional
from enhanced_quantum_backend_selector.scoring_weights import ScoringWeights

@dataclass
class ScoringConfiguration:
    """User-configurable parameters for transpiled circuit scoring."""
    
    transpilation_runs: int = 3
    aggregation_method: str = 'mean'
    fractional_gates_mode: str = 'both'
    optimization_level: int = 3
    weights: Optional[ScoringWeights] = None
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Validate transpilation_runs
        if self.transpilation_runs <= 0:
            raise ValueError(
                f"transpilation_runs must be positive integer, got {self.transpilation_runs}"
            )
        
        # Validate aggregation_method
        valid_methods = ['mean', 'median', 'minimum']
        if self.aggregation_method not in valid_methods:
            raise ValueError(
                f"aggregation_method must be one of {valid_methods}, "
                f"got '{self.aggregation_method}'"
            )
        
        # Validate fractional_gates_mode
        valid_modes = ['both', 'enabled', 'disabled']
        if self.fractional_gates_mode not in valid_modes:
            raise ValueError(
                f"fractional_gates_mode must be one of {valid_modes}, "
                f"got '{self.fractional_gates_mode}'"
            )
        
        # Validate optimization_level
        if not (0 <= self.optimization_level <= 3):
            raise ValueError(
                f"optimization_level must be 0-3, got {self.optimization_level}"
            )
```

**Usage Example**:

```python
# Default configuration (backward compatible)
config = ScoringConfiguration()

# Custom configuration
custom_config = ScoringConfiguration(
    transpilation_runs=5,
    aggregation_method='median',
    fractional_gates_mode='enabled',
    optimization_level=2
)

# Validation happens automatically
try:
    bad_config = ScoringConfiguration(transpilation_runs=0)
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Modified Entities

### 4. BackendRecommendation (Extended)

**Modification**: Add fields for transpilation transparency.

**New Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `transpilation_details` | `Optional[AggregatedScore]` | Aggregated transpilation scores (None if excluded) |
| `fractional_gates_used` | `Optional[bool]` | Which fractional gates config was used (None if both) |

**Modified Implementation**:

```python
@dataclass
class BackendRecommendation:
    """Recommendation for a specific backend with scoring details."""
    
    backend: BackendV2
    score_data: CircuitScore
    rank: int
    is_compatible: bool
    incompatibility_reason: Optional[str] = None
    
    # NEW FIELDS for transpilation transparency
    transpilation_details: Optional[AggregatedScore] = None
    fractional_gates_used: Optional[bool] = None
```

**Backward Compatibility**: 
- All new fields are `Optional` with `None` defaults
- Existing code continues to work without modification
- New fields only populated when transpilation scoring is used

---

## Entity Relationships

```
ScoringConfiguration
    ↓ (configures)
Backend Selector
    ↓ (for each backend)
Multiple TranspilationRun instances
    ↓ (aggregated by)
AggregatedScore
    ↓ (attached to)
BackendRecommendation
    ↓ (ranked list returned to)
User
```

**Flow**:
1. User provides `ScoringConfiguration` (or uses defaults)
2. Backend selector transpiles circuit multiple times per backend → `TranspilationRun` objects
3. Runs aggregated into `AggregatedScore` using configured method
4. `AggregatedScore` attached to `BackendRecommendation`
5. Recommendations ranked and returned to user

---

## Type Hierarchy

```
models.py (existing)
├── BackendMetrics (existing)
├── CircuitScore (existing)
├── BackendRecommendation (modified - add transpilation fields)
└── [NEW ENTITIES]
    ├── TranspilationRun
    ├── AggregatedScore
    └── ScoringConfiguration
```

All entities are dataclasses with:
- Strong typing (constitution principle I)
- Validation in `__post_init__` 
- Optional fields use `Optional[T]` type hints
- Helper methods as classmethods (e.g., `AggregatedScore.from_runs`)

---

## Import Structure

```python
# In models.py
from dataclasses import dataclass, field
from typing import List, Optional
from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2
from statistics import mean, median, stdev, variance

# Public API exports
__all__ = [
    'BackendMetrics',
    'CircuitScore',
    'BackendRecommendation',
    'TranspilationRun',          # NEW
    'AggregatedScore',           # NEW
    'ScoringConfiguration',      # NEW
]
```

---

## Validation Rules Summary

| Entity | Validation Rules |
|--------|------------------|
| TranspilationRun | success=True requires error_sum; success=False requires failure_reason |
| AggregatedScore | individual_scores length must match successful_runs; method must be valid |
| ScoringConfiguration | transpilation_runs > 0; method in {mean, median, minimum}; mode in {both, enabled, disabled}; optimization_level 0-3 |
| BackendRecommendation | No new validations (optional fields) |

All validations raise `ValueError` with descriptive messages.

---

## Testing Considerations

Each entity requires unit tests for:

1. **TranspilationRun**:
   - Successful run creation
   - Failed run creation
   - Validation of success/error_sum relationship
   - Validation of failure_reason requirement

2. **AggregatedScore**:
   - Creation from TranspilationRun list
   - Mean/median/minimum aggregation correctness
   - Variance/std_dev calculation
   - Handling single vs multiple runs
   - Validation of score count vs successful_runs

3. **ScoringConfiguration**:
   - Default values correct
   - Validation of transpilation_runs (positive integer)
   - Validation of aggregation_method (valid options)
   - Validation of fractional_gates_mode (valid options)
   - Validation of optimization_level (0-3 range)

4. **BackendRecommendation** (modified):
   - Backward compatibility (works without new fields)
   - New fields populated correctly
   - Optional fields handle None gracefully

---

## Phase 1 Sign-off

**Data Model Status**: ✅ **COMPLETE**  
**Ready for Phase 2**: Pending API contracts and quickstart  
**Blockers**: None

**Next Deliverable**: `contracts/scoring_api.md` documenting API methods and helper functions.
