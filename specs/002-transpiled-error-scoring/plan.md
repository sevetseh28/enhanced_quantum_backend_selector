# Implementation Plan: Transpiled Circuit Error-Based Scoring

**Branch**: `002-transpiled-error-scoring` | **Date**: December 11, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-transpiled-error-scoring/spec.md`

## Summary

Update the quantum backend selector's scoring mechanism to use transpiled circuits instead of source circuits for error rate calculation. The system will transpile each circuit multiple times (default 3) to account for stochastic transpilation behavior, sum instruction-specific error rates from backend calibration data, and aggregate results using statistical measures (mean by default). Support for fractional gates configuration evaluation (both enabled/disabled by default, user-configurable) enables comprehensive backend assessment across different operational modes. This provides realistic error predictions based on what actually executes on quantum hardware.

## Technical Context

**Language/Version**: Python 3.12 (as specified in pyproject.toml and devcontainer)
**Primary Dependencies**: 
- Qiskit (>=1.0.0): Transpiler, BackendV2, Target, QuantumCircuit
- Existing: pydantic for data models, dataclasses for lightweight structures

**Storage**: In-memory caching (1-hour TTL) for backend calibration data only (not transpiled circuits)
**Testing**: pytest with ≥80% coverage requirement, integration tests with Qiskit Aer and fake backends
**Target Platform**: Python library for Linux/macOS/Windows (platform-agnostic)
**Project Type**: Single Python package (enhanced_quantum_backend_selector)
**Performance Goals**: 
- Backend ranking completes within 10 seconds for 10 backends with multiple transpilation runs and fractional gate configs
- Transpilation overhead acceptable compared to backend API latency

**Constraints**:
- Must maintain backward compatibility (no breaking API changes)
- Must work with any Qiskit BackendV2 provider (provider-agnostic)
- Must preserve existing 1-hour cache TTL for backend metrics
- Must respect constitution principles (strong typing, comprehensive testing, code simplicity)

**Scale/Scope**: 
- Modify 1-2 core files (backend_selector.py, possibly backend_analyzer.py)
- Add/update 2-3 data models in models.py
- Expand test coverage for new transpilation logic
- ~500-800 lines of new/modified code estimated

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Strong Typing (NON-NEGOTIABLE)
- All new transpilation functions will have explicit type hints
- ScoringConfiguration dataclass will include typed fields for transpilation_runs, aggregation_method, fractional_gates_mode
- TranspilationRun and AggregatedScore models will be strongly typed
- No use of `Any` type except where Qiskit APIs require it (with justification comments)

### ✅ Principle II: Comprehensive Testing & CI/CD
- Unit tests for transpilation logic (mocked backends)
- Integration tests with Qiskit Aer and fake backends
- Test all aggregation methods (mean, median, minimum)
- Test fractional gates configurations (both, enabled-only, disabled-only)
- Test edge cases: transpilation failures, missing calibration data, zero-instruction circuits
- Target ≥80% coverage maintained

### ✅ Principle III: Semantic Versioning
- This is a MINOR version bump (new features, backward compatible)
- Public API signatures preserved (existing methods unchanged)
- New optional parameters added with sensible defaults
- CHANGELOG.md will document: transpiled circuit scoring, multi-run aggregation, fractional gates support

### ✅ Principle IV: Code Formatting & Style
- Ruff formatting enforced via pre-commit hooks
- Maximum 100-character line length
- Google-style docstrings for all new functions
- Import organization: stdlib → third-party → local

### ✅ Principle V: Extensive Documentation
- Docstrings for all new/modified public methods
- Examples showing transpilation configuration options
- Updated user guide explaining transpiled scoring benefits
- Architecture notes on transpilation caching strategy

### ✅ Principle VI: Code Simplicity
- Extract transpilation logic into focused helper functions (<50 lines each)
- Avoid nesting beyond 3 levels (use early returns)
- One class per file rule maintained
- Data models separated in models.py
- Cyclomatic complexity kept <10 per function

### ✅ Principle VII: Provider Agnostic Design
- All backend interactions through BackendV2 and Target interfaces
- Graceful handling of missing calibration data (different providers supply different metrics)
- No IBM Quantum-specific assumptions
- Tests validate against multiple backend types

**Constitution Compliance**: ✅ **ALL GATES PASS** - No violations or complexity debt

## Project Structure

### Documentation (this feature)

```text
specs/002-transpiled-error-scoring/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Research Qiskit transpiler APIs, error rate retrieval
├── data-model.md        # Phase 1: TranspilationRun, AggregatedScore, ScoringConfiguration
├── quickstart.md        # Phase 1: Usage examples for new scoring features
├── contracts/           # Phase 1: API contracts (if external interfaces added)
│   └── scoring_api.md   # Document new scoring configuration parameters
├── checklists/
│   └── requirements.md  # Quality checklist (completed)
└── tasks.md             # Phase 2: Detailed implementation tasks (generated by /speckit.tasks)
```

### Source Code (repository root)

```text
enhanced-quantum-backend-selector/
├── src/enhanced_quantum_backend_selector/
│   ├── __init__.py
│   ├── backend_selector.py          # MODIFY: Add transpilation + aggregation logic
│   ├── models.py                     # MODIFY: Add TranspilationRun, AggregatedScore, ScoringConfiguration
│   ├── scoring_weights.py            # NO CHANGE: Existing weights system preserved
│   └── exploration/
│       ├── backend_analyzer.py       # MODIFY: Add error rate extraction from Target
│       └── ... (other exploration files unchanged)
├── tests/
│   ├── test_backend_selector.py      # MODIFY: Add transpilation + aggregation tests
│   ├── test_integration.py           # MODIFY: Add multi-backend fractional gates tests
│   ├── test_transpilation.py         # NEW: Dedicated transpilation logic tests
│   └── fixtures/
│       ├── canonical_circuits.py      # EXTEND: Add circuits for transpilation testing
│       └── ... (other fixtures)
├── examples/
│   ├── basic_usage.py                # MODIFY: Add transpilation configuration example
│   └── advanced_usage.py             # MODIFY: Show fractional gates + aggregation options
├── docs/
│   ├── user-guide.md                 # MODIFY: Explain new scoring mechanism
│   ├── api-reference.md              # MODIFY: Document new parameters/models
│   └── architecture.md               # MODIFY: Add transpilation flow diagram
├── pyproject.toml                    # NO CHANGE: Dependencies remain same
└── README.md                         # MODIFY: Update feature list with transpiled scoring
```

**Structure Decision**: Single project structure maintained. All changes confined to existing `src/enhanced_quantum_backend_selector/` package. No new top-level directories or projects needed. Modifications focused on `backend_selector.py` (orchestration), `models.py` (data structures), and `exploration/backend_analyzer.py` (error rate extraction).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected** - Constitution check passes fully. No complexity debt introduced.

---

## Phase 0: Outline & Research

### Research Objectives

1. **Qiskit Transpiler API**: Investigate transpile() function, optimization levels, stochastic behavior control
2. **Target Error Rates**: Document how to extract per-instruction, per-qubit error rates from Target.instruction_properties
3. **Fractional Gates**: Research BackendV2.target() method with use_fractional_gates parameter
4. **Transpilation Failures**: Catalog common failure modes and exception types
5. **Performance Profiling**: Measure transpilation time vs backend API call latency to validate assumptions

### Research Questions to Resolve

- **Q1**: What Qiskit API retrieves error rates for a specific instruction on specific qubits from a Target?
  - Expected: `target.instruction_properties(instruction_name).get((qubit_tuple,)).error`

- **Q2**: How to pass fractional gates flag to transpiler? Does it require custom Target or PassManager?
  - Expected: Pass `backend.target(use_fractional_gates=True/False)` to transpile()

- **Q3**: What exceptions does qiskit.transpile() raise on failure? How to catch and log gracefully?
  - Expected: TranspilerError, possibly QiskitError subclasses

- **Q4**: How to ensure transpilation stochasticity? Does default optimization_level provide sufficient variability?
  - Expected: optimization_level=3 provides stochasticity; may need to verify seed behavior

- **Q5**: What's the performance impact of 3 transpilations × 2 fractional configs × 10 backends = 60 transpilations?
  - Target: <10 seconds total (as per SC-005)

### Research Deliverables

Create `specs/002-transpiled-error-scoring/research.md` with:
- Code snippets demonstrating error rate extraction from Target
- Transpilation API examples with fractional gates
- Performance benchmarks for transpilation operations
- Exception handling patterns
- Decision: Confirm mean aggregation as default (from clarifications)
- Decision: Confirm cache backend calibration only, not transpiled circuits (from clarifications)

---

## Phase 1: Design & Contracts

### Data Model (`data-model.md`)

**New Entities**:

```python
@dataclass
class TranspilationRun:
    """Single transpilation attempt result."""
    circuit: QuantumCircuit          # Transpiled circuit
    success: bool                     # Whether transpilation succeeded
    error_sum: Optional[float]        # Sum of instruction error rates (None if failed)
    failure_reason: Optional[str]     # Error message if failed
    fractional_gates: bool            # Which config was used

@dataclass
class AggregatedScore:
    """Score aggregated from multiple transpilation runs."""
    final_score: float                # Aggregated error sum
    individual_scores: List[float]    # Error sums from each successful run
    aggregation_method: str           # 'mean', 'median', or 'minimum'
    successful_runs: int              # Count of successful transpilations
    failed_runs: int                  # Count of failed transpilations
    variance: Optional[float]         # Statistical variance (if applicable)

@dataclass
class ScoringConfiguration:
    """User-configurable scoring parameters."""
    transpilation_runs: int = 3                    # Number of transpilation attempts
    aggregation_method: str = 'mean'               # 'mean', 'median', or 'minimum'
    fractional_gates_mode: str = 'both'            # 'both', 'enabled', 'disabled'
    weights: Optional[ScoringWeights] = None       # Existing weights system
```

**Modified Entities**:

```python
@dataclass
class BackendRecommendation:
    """Extended to include transpilation details."""
    backend: BackendV2
    score_data: CircuitScore
    rank: int
    is_compatible: bool
    incompatibility_reason: Optional[str]
    # NEW FIELDS:
    transpilation_details: Optional[AggregatedScore] = None
    fractional_gates_used: Optional[bool] = None
```

### API Contracts (`contracts/scoring_api.md`)

**Modified Methods** (backward compatible with new optional parameters):

```python
# backend_selector.py

def select_backend(
    self,
    circuit: QuantumCircuit,
    weights: Optional[ScoringWeights] = None,
    require_compatible: bool = True,
    min_score: Optional[float] = None,
    # NEW PARAMETERS (optional with defaults):
    config: Optional[ScoringConfiguration] = None,  # Default: 3 runs, mean, both fractional
) -> BackendRecommendation:
    """
    Select best backend using transpiled circuit error scoring.
    
    New Behavior:
    - Transpiles circuit multiple times per backend (config.transpilation_runs)
    - Evaluates fractional gates configs based on config.fractional_gates_mode
    - Aggregates scores using config.aggregation_method
    - Returns transpilation_details in recommendation
    """

def rank_backends(
    self,
    circuit: QuantumCircuit,
    weights: Optional[ScoringWeights] = None,
    config: Optional[ScoringConfiguration] = None,  # NEW
) -> List[BackendRecommendation]:
    """
    Rank all backends using transpiled circuit error scoring.
    
    New Behavior: Same transpilation + aggregation as select_backend
    """
```

**Internal Helper Functions** (new):

```python
def _transpile_circuit(
    circuit: QuantumCircuit,
    backend: BackendV2,
    use_fractional_gates: bool,
) -> QuantumCircuit:
    """Transpile circuit to backend's native gate set."""

def _calculate_error_sum(
    transpiled_circuit: QuantumCircuit,
    backend: BackendV2,
) -> float:
    """Sum instruction error rates from backend calibration."""

def _aggregate_scores(
    runs: List[TranspilationRun],
    method: str,
) -> AggregatedScore:
    """Aggregate error sums using statistical measure."""
```

### Quickstart Guide (`quickstart.md`)

**Basic Usage** (backward compatible):
```python
from enhanced_quantum_backend_selector import BackendSelector
from qiskit import QuantumCircuit

# Works exactly as before (uses new transpiled scoring internally)
selector = BackendSelector(backends)
recommendation = selector.select_backend(my_circuit)
```

**Advanced Configuration** (new features):
```python
from enhanced_quantum_backend_selector import BackendSelector, ScoringConfiguration

# Customize transpilation behavior
config = ScoringConfiguration(
    transpilation_runs=5,           # More runs for higher confidence
    aggregation_method='median',    # Robust to outliers
    fractional_gates_mode='enabled' # Only test with fractional gates
)

recommendation = selector.select_backend(my_circuit, config=config)

# Inspect transpilation details
print(f"Successful runs: {recommendation.transpilation_details.successful_runs}")
print(f"Error variance: {recommendation.transpilation_details.variance}")
```

### Agent Context Update

After Phase 1 completion, run:
```bash
.specify/scripts/bash/update-agent-context.sh copilot
```

This will update `.github/copilot-instructions.md` with:
- New data models (TranspilationRun, AggregatedScore, ScoringConfiguration)
- Modified API surface (config parameter)
- Transpilation workflow overview

---

## Phase 2: Task Breakdown

**This section intentionally left incomplete** - Tasks will be generated by `/speckit.tasks` command after Phase 0 and Phase 1 are complete. The command will create `specs/002-transpiled-error-scoring/tasks.md` with:

- Atomic implementation tasks broken down by file
- Test coverage requirements per task
- Dependencies between tasks
- Estimated complexity/effort
- Acceptance criteria per task

**Prerequisite for /speckit.tasks**:
- ✅ research.md completed with technical findings
- ✅ data-model.md finalized with entity specifications  
- ✅ contracts/ directory populated with API contracts
- ✅ quickstart.md showing usage examples

---

## Phase 3: Implementation

**Not started** - This phase begins after `/speckit.tasks` generates the task list.

**Implementation order** (preliminary, will be refined in tasks.md):
1. Add data models to models.py (TranspilationRun, AggregatedScore, ScoringConfiguration)
2. Implement transpilation helpers (_transpile_circuit, _calculate_error_sum)
3. Implement aggregation logic (_aggregate_scores)
4. Modify backend_selector.py to use transpiled scoring
5. Update backend_analyzer.py for error rate extraction
6. Add comprehensive tests
7. Update documentation and examples
8. Validate backward compatibility

---

## Phase 4: Validation & Completion

**Validation Checklist** (run before marking feature complete):

### Functional Validation
- [ ] All FR-001 through FR-019 requirements met
- [ ] All user stories (P1, P2) testable and passing
- [ ] All edge cases handled as specified
- [ ] Backward compatibility verified (existing code works unchanged)

### Quality Gates
- [ ] Test coverage ≥80% (pytest-cov)
- [ ] All tests passing (pytest)
- [ ] Type checking passes (mypy --strict)
- [ ] Linting passes (ruff check)
- [ ] Formatting passes (ruff format --check)

### Performance Validation
- [ ] SC-005: 10 backends scored in <10 seconds with 3 runs × 2 configs
- [ ] SC-002: Variance reduction ≥30% vs single transpilation run (empirical test)

### Documentation Validation
- [ ] All public API methods have docstrings
- [ ] Examples in docs/ directory execute successfully
- [ ] CHANGELOG.md updated with feature description
- [ ] README.md updated to mention transpiled scoring

### Constitution Re-Check
- [ ] All 7 principles still satisfied
- [ ] No new complexity debt introduced
- [ ] DevContainer configuration still accurate

---

## Success Metrics

From Success Criteria in spec.md:

1. **SC-001**: Backend scores use transpiled circuit error sums ✓
2. **SC-002**: Mean of 3 runs reduces variance ≥30% ✓  
3. **SC-003**: Fractional gates configs clearly distinguished ✓
4. **SC-004**: ≥95% circuit compatibility across IBM backends ✓
5. **SC-005**: Ranking 10 backends completes in <10 seconds ✓
6. **SC-006**: Backward compatibility maintained ✓
7. **SC-007**: Transpilation details transparent in results ✓

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Transpilation too slow | Medium | High | Profile early in Phase 0; parallelize if needed with ThreadPoolExecutor |
| Some backends missing error rate data | High | Medium | Already handled per FR-009 (skip with warning, continue scoring) |
| Fractional gates API changes in Qiskit | Low | High | Research in Phase 0; version pin if unstable |
| Backward compatibility broken accidentally | Low | Critical | Comprehensive integration tests with existing examples |
| Aggregation introduces unexpected bias | Low | Medium | Validate statistically in Phase 4; configurable to allow user override |

---

## Open Questions

*To be resolved in Phase 0 research:*

1. Does Qiskit's transpile() provide sufficient stochasticity by default, or do we need to manipulate seeds?
2. What's the actual performance overhead of 60+ transpilations? (Need empirical data)
3. Are there Qiskit version compatibility issues with fractional gates in BackendV2.target()?
4. Should we expose per-run details to users, or only aggregated scores?

*Clarified during spec phase:*
- ✅ Aggregation method: Mean (with median/min as alternatives)
- ✅ Fractional gates: User-configurable with "both" as default
- ✅ Caching strategy: Backend calibration only, not transpiled circuits
- ✅ Qubit count compatibility: Attempt all backends, let transpiler decide
- ✅ All transpilation failures: Exclude backend from ranking with detailed reason

---

**Next Command**: Execute Phase 0 research by implementing the research objectives above and documenting findings in `specs/002-transpiled-error-scoring/research.md`.
