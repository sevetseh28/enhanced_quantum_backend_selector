# Tasks: Transpiled Circuit Error-Based Scoring

**Feature**: `002-transpiled-error-scoring`  
**Input**: Design documents from `/specs/002-transpiled-error-scoring/`  
**Generated**: December 11, 2025

**Prerequisites**: ✅ plan.md, ✅ spec.md, ✅ research.md, ✅ data-model.md, ✅ contracts/, ✅ quickstart.md

**Tests**: Not requested in feature specification - tests are OPTIONAL for this feature

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: `- [ ]` for all tasks
- **[ID]**: Sequential task number (T001, T002, ...)
- **[P]**: Optional marker for parallelizable tasks (different files, no dependencies)
- **[Story]**: Story label (US1, US2, US3) for user story phases only
- **Description**: Clear action with exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare branch and ensure development environment is ready

- [ ] T001 Create feature branch `002-transpiled-error-scoring` from main
- [ ] T002 Verify Python 3.12 environment activated (Poetry venv)
- [ ] T003 Verify Qiskit 2.0+ and qiskit_ibm_runtime installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Add TranspilationRun dataclass to src/enhanced_quantum_backend_selector/models.py
- [ ] T005 [P] Add AggregatedScore dataclass with from_runs classmethod to src/enhanced_quantum_backend_selector/models.py
- [ ] T006 [P] Add ScoringConfiguration dataclass with validation in __post_init__ to src/enhanced_quantum_backend_selector/models.py
- [ ] T007 Extend BackendRecommendation dataclass with transpilation_details and fractional_gates_used fields in src/enhanced_quantum_backend_selector/models.py
- [ ] T008 [P] Update __all__ exports in src/enhanced_quantum_backend_selector/__init__.py to include new models
- [ ] T009 [P] Add _get_backend_calibration method with 1-hour TTL caching to src/enhanced_quantum_backend_selector/backend_selector.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Accurate Backend Scoring with Transpiled Circuits (Priority: P1) 🎯 MVP

**Goal**: Score backends based on transpiled circuits with instruction-specific error rates, not source circuits

**Independent Test**: Provide source circuit → transpile to backend → extract error rates per instruction/qubit → sum errors → compare to backend score. Delivers realistic error predictions.

### Implementation for User Story 1

- [ ] T010 [P] [US1] Add _transpile_circuit helper method in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T011 [P] [US1] Add _calculate_error_sum helper method in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T012 [US1] Implement _score_backend_with_transpilation orchestrator method in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T013 [US1] Modify select_backend to accept optional config parameter and use transpiled scoring in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T014 [US1] Modify rank_backends to accept optional config parameter and use transpiled scoring in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T015 [US1] Add backend exclusion logging for failed transpilations in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T016 [US1] Add warning logging for missing instruction error data in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T017 [US1] Handle TranspilerError exceptions in _transpile_circuit with TranspilationRun failure objects in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T018 [US1] Handle identity circuits (zero instructions) with perfect score (0.0 error sum) in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T019 [US1] Validate and raise ValueError when all backends fail transpilation in select_backend/rank_backends in src/enhanced_quantum_backend_selector/backend_selector.py

**Checkpoint**: At this point, User Story 1 should be fully functional - transpiled circuit scoring works end-to-end

---

## Phase 4: User Story 2 - Stochastic Transpilation Handling (Priority: P2)

**Goal**: Run multiple transpilations per backend and aggregate scores to account for transpiler variability

**Independent Test**: Transpile same circuit 3+ times → calculate error scores for each → aggregate using mean/median/minimum → verify final score derived from multiple samples. Reduces selection variance.

### Implementation for User Story 2

- [ ] T020 [P] [US2] Add _aggregate_scores helper method with mean/median/minimum support in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T021 [US2] Update _score_backend_with_transpilation to loop config.transpilation_runs times in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T022 [US2] Implement parallelization with ThreadPoolExecutor for multiple transpilations within backend in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T023 [US2] Calculate variance and std_dev in AggregatedScore.from_runs method in src/enhanced_quantum_backend_selector/models.py
- [ ] T024 [US2] Handle partial failures (some runs succeed, some fail) in _aggregate_scores in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T025 [US2] Return None from _score_backend_with_transpilation if all runs failed in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T026 [US2] Validate ScoringConfiguration.transpilation_runs is positive integer in __post_init__ in src/enhanced_quantum_backend_selector/models.py
- [ ] T027 [US2] Validate ScoringConfiguration.aggregation_method is in ['mean', 'median', 'minimum'] in __post_init__ in src/enhanced_quantum_backend_selector/models.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - multi-run aggregation reduces variance

---

## Phase 5: User Story 3 - Fractional Gates Configuration Support (Priority: P2)

**Goal**: Evaluate backends with fractional gates enabled/disabled/both to find best configuration per circuit

**Independent Test**: Retrieve backend target with fractional_gates=True vs False → transpile same circuit under both configs → verify separate scores calculated for each. Reveals optimal operational mode.

### Implementation for User Story 3

- [ ] T028 [P] [US3] Research and document fractional gates parameter API in backend.target() or transpile() in specs/002-transpiled-error-scoring/research.md
- [ ] T029 [US3] Add fractional_gates parameter to _transpile_circuit method signature in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T030 [US3] Implement fractional gates mode 'both' logic in _score_backend_with_transpilation (double transpilations) in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T031 [US3] Implement fractional gates mode 'enabled' logic (single config) in _score_backend_with_transpilation in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T032 [US3] Implement fractional gates mode 'disabled' logic (single config) in _score_backend_with_transpilation in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T033 [US3] Compare scores from both fractional gate configs and select best in _score_backend_with_transpilation in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T034 [US3] Set fractional_gates_used field in BackendRecommendation based on selected config in src/enhanced_quantum_backend_selector/backend_selector.py
- [ ] T035 [US3] Validate ScoringConfiguration.fractional_gates_mode is in ['both', 'enabled', 'disabled'] in __post_init__ in src/enhanced_quantum_backend_selector/models.py
- [ ] T036 [US3] Handle backends that don't support fractional gates gracefully (log warning, continue) in src/enhanced_quantum_backend_selector/backend_selector.py

**Checkpoint**: All user stories should now be independently functional - comprehensive backend evaluation complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize feature

- [ ] T037 [P] Update basic_usage.py example to show default transpiled scoring in examples/basic_usage.py
- [ ] T038 [P] Update advanced_usage.py example with ScoringConfiguration options in examples/advanced_usage.py
- [ ] T039 [P] Add example showing aggregation methods (mean/median/minimum) in examples/advanced_usage.py
- [ ] T040 [P] Add example showing fractional gates modes in examples/advanced_usage.py
- [ ] T041 [P] Update user-guide.md explaining transpiled scoring benefits in docs/user-guide.md
- [ ] T042 [P] Update api-reference.md documenting new config parameter and models in docs/api-reference.md
- [ ] T043 [P] Update architecture.md with transpilation flow diagram in docs/architecture.md
- [ ] T044 [P] Add CHANGELOG.md entry describing new features in enhanced-quantum-backend-selector/CHANGELOG.md
- [ ] T045 [P] Update README.md feature list with transpiled scoring in enhanced-quantum-backend-selector/README.md
- [ ] T046 Run validate_examples.py to ensure all examples execute successfully
- [ ] T047 Run ruff format on all modified files to ensure formatting compliance
- [ ] T048 Run ruff check on all modified files to ensure linting compliance
- [ ] T049 Run mypy on src/enhanced_quantum_backend_selector/ for type checking validation
- [ ] T050 Verify backward compatibility by running existing examples without config parameter
- [ ] T051 Performance validation: rank 10 backends with 3 runs in < 10 seconds (SC-005)
- [ ] T052 Validate all 19 functional requirements (FR-001 through FR-019) are met
- [ ] T053 Final constitution check: verify all 7 principles still satisfied

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) AND User Story 1 (Phase 3) - extends transpilation with aggregation
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) AND User Story 1 (Phase 3) - extends transpilation with fractional gates
- **Polish (Phase 6)**: Depends on all user stories (Phases 3-5) being complete

### User Story Dependencies

```
Foundational (Phase 2)
    ↓
User Story 1 (Phase 3) ← MVP Baseline
    ↓             ↓
    ↓         User Story 3 (Phase 5)
    ↓             ↓
User Story 2 (Phase 4)
    ↓
Polish (Phase 6)
```

- **User Story 1 (P1)**: Foundation for all other stories - implements core transpilation logic
- **User Story 2 (P2)**: Extends US1 with multi-run aggregation - can be tested independently
- **User Story 3 (P2)**: Extends US1 with fractional gates support - can be tested independently
- **User Story 2 and 3**: Can be worked in parallel after US1 completes

### Within Each User Story

- **US1**: T010-T011 [P] parallel → T012 orchestrates → T013-T014 modify public API → T015-T019 error handling
- **US2**: T020 [P], T023 [P], T026-T027 [P] parallel → T021-T022 integrate → T024-T025 error handling
- **US3**: T028 research first → T029 update signature → T030-T036 implement modes sequentially

### Parallel Opportunities

**Phase 2 (Foundational)**:
```bash
# All dataclass additions can be done in parallel
T004 (TranspilationRun) || T005 (AggregatedScore) || T006 (ScoringConfiguration) || T007 (BackendRecommendation extension)
# Then independently:
T008 (__all__ exports) || T009 (caching)
```

**Phase 3 (User Story 1)**:
```bash
# Core helpers can be done in parallel
T010 (_transpile_circuit) || T011 (_calculate_error_sum)
# Then sequentially:
T012 (_score_backend_with_transpilation) → T013-T014 (public API) → T015-T019 (error handling)
```

**Phase 4 (User Story 2)**:
```bash
# Independent pieces in parallel
T020 (_aggregate_scores) || T023 (variance calc) || T026-T027 (validation)
# Then:
T021-T022 (integration) → T024-T025 (error handling)
```

**Phase 6 (Polish)**:
```bash
# All documentation updates can be done in parallel
T037 (basic_usage) || T038 (advanced_usage) || T039 (aggregation example) || T040 (fractional example)
T041 (user-guide) || T042 (api-reference) || T043 (architecture) || T044 (CHANGELOG) || T045 (README)
# Then sequential validation:
T046 → T047 → T048 → T049 → T050 → T051 → T052 → T053
```

---

## Parallel Example: User Story 1

```bash
# Day 1: Foundation
git checkout -b 002-transpiled-error-scoring  # T001
# T002-T003 verify environment

# T004-T007 in parallel (different models)
Developer A: Add TranspilationRun + AggregatedScore (T004-T005)
Developer B: Add ScoringConfiguration + extend BackendRecommendation (T006-T007)

# Day 2: Core Implementation
# T008-T009 quick updates
git pull --rebase  # Merge foundation work

# T010-T011 in parallel (different methods)
Developer A: Implement _transpile_circuit (T010)
Developer B: Implement _calculate_error_sum (T011)

# Day 3: Integration
git pull --rebase
# T012 (one developer, orchestrates T010+T011)
Developer A: Implement _score_backend_with_transpilation (T012)

# T013-T014 in parallel
Developer A: Modify select_backend (T013)
Developer B: Modify rank_backends (T014)

# Day 4: Error Handling
git pull --rebase
# T015-T019 sequential (error handling logic interrelated)
Developer A: Add logging, exception handling, validation (T015-T019)

# US1 Complete ✓
```

**Time Estimate**: 3-4 days for User Story 1 (MVP baseline)

---

## Parallel Example: Full Feature (3 Developers)

```bash
# Week 1: Foundation + US1
Dev1: Phase 1 Setup (T001-T003)
All:  Phase 2 Foundational (T004-T009) - parallel dataclasses
All:  Phase 3 US1 (T010-T019) - parallel helpers, then integration

# Week 2: US2 + US3 in parallel
Dev1: Phase 4 US2 (T020-T027) - Aggregation logic
Dev2: Phase 5 US3 (T028-T036) - Fractional gates research + implementation
Dev3: Start Phase 6 documentation (T037-T045) in parallel

# Week 3: Polish + Validation
Dev1: Finish US2 (T020-T027)
Dev2: Finish US3 (T028-T036)
Dev3: Continue Phase 6 documentation (T037-T045)
All:  Phase 6 validation (T046-T053) - sequential checks

# Feature Complete ✓
```

**Time Estimate**: 2-3 weeks for full feature with 3 developers

---

## Implementation Strategy

### MVP First (Recommended)

**Week 1: Deliver User Story 1 Only**
- ✅ Phases 1-3 complete (T001-T019)
- ✅ Transpiled circuit scoring works end-to-end
- ✅ Single transpilation run per backend (config.transpilation_runs=1 default)
- ✅ No fractional gates support yet
- ✅ Users can immediately benefit from realistic error predictions

**Value**: Delivers core improvement (accurate scoring) with minimal complexity. Can be released as v0.1.0 with "stochastic handling coming soon".

### Incremental Delivery

**Week 2: Add User Story 2**
- ✅ Phases 4 complete (T020-T027)
- ✅ Multi-run aggregation reduces variance
- ✅ Users can configure transpilation_runs and aggregation_method
- ✅ Release as v0.2.0

**Week 3: Add User Story 3**
- ✅ Phases 5 complete (T028-T036)
- ✅ Fractional gates evaluation comprehensive
- ✅ Users can evaluate all operational modes
- ✅ Release as v1.0.0 (full feature complete)

### All-at-Once Delivery

**Weeks 1-3: Implement All Stories**
- ✅ Phases 1-6 complete (T001-T053)
- ✅ Full feature with all capabilities
- ✅ Release as v1.0.0

**Risk**: Longer time to first value delivery, but more cohesive initial release.

---

## Task Complexity Estimates

| Phase | Task Count | Total Lines | Estimated Hours | Dependencies |
|-------|-----------|-------------|-----------------|--------------|
| Phase 1: Setup | 3 | 0 | 0.5h | None |
| Phase 2: Foundational | 6 | ~150 | 4-6h | Phase 1 |
| Phase 3: US1 (MVP) | 10 | ~250 | 12-16h | Phase 2 |
| Phase 4: US2 | 8 | ~150 | 8-12h | Phase 2, Phase 3 |
| Phase 5: US3 | 9 | ~200 | 10-14h | Phase 2, Phase 3 |
| Phase 6: Polish | 17 | ~100 | 8-10h | Phases 3-5 |
| **TOTAL** | **53** | **~850** | **42-58h** | Sequential or parallel |

**Notes**:
- Line counts include dataclasses, methods, docstrings, error handling
- Hours assume experienced Python/Qiskit developer
- Parallelization can reduce calendar time to ~2-3 weeks with 2-3 developers
- Sequential implementation: ~6-8 weeks for single developer

---

## Testing Strategy (Optional - Not Requested)

While tests were not explicitly requested in the feature specification, the following test structure is recommended if quality gates require ≥80% coverage:

### Unit Tests (if needed)

- **test_models.py**: Validate dataclass validation, AggregatedScore.from_runs, ScoringConfiguration defaults
- **test_transpilation.py**: Mock transpile(), test _transpile_circuit error handling, test _calculate_error_sum with mocked Target
- **test_aggregation.py**: Test _aggregate_scores with mean/median/minimum, test variance calculation

### Integration Tests (if needed)

- **test_backend_selector.py**: Extend existing tests with config parameter, verify transpilation_details in recommendations
- **test_integration.py**: End-to-end with Fake backends, test fractional gates modes, test multi-run aggregation

### Validation Tests (recommended)

- **examples/validate_examples.py**: Already exists - run to ensure examples work (T046)
- **Performance test**: Rank 10 backends in <10s (T051)

---

## Validation Checklist (Before PR/Merge)

### Functional Requirements ✓

- [ ] FR-001: Circuit transpiled to native gates before scoring
- [ ] FR-002: Error sum calculated from transpiled instructions
- [ ] FR-003: Error rates retrieved from backend.target[operation][qubits].error
- [ ] FR-004: Multiple transpilation runs per backend (default 3)
- [ ] FR-005: Aggregation methods: mean (default), median, minimum
- [ ] FR-006: Fractional gates mode: both (default), enabled, disabled
- [ ] FR-007: Both fractional configs evaluated by default when supported
- [ ] FR-008: Missing error data handled gracefully with warnings
- [ ] FR-009: (duplicate of FR-008)
- [ ] FR-010: Configurable transpilation run count (validated positive integer)
- [ ] FR-011: Successful/failed run counts reported in AggregatedScore
- [ ] FR-012: Backends excluded from ranking when all runs fail (with detailed reason)
- [ ] FR-013: Backend calibration cached (1-hour TTL), transpiled circuits not cached
- [ ] FR-014: All backends attempted regardless of qubit count
- [ ] FR-015: Qubit count not a scoring factor (only compatibility check)
- [ ] FR-016: Backward compatibility maintained (no breaking API changes)
- [ ] FR-017: Existing scoring weights system preserved
- [ ] FR-018: Identity circuits (zero instructions) get perfect score (0.0)
- [ ] FR-019: Deterministic ranking with secondary sort (backend name)

### Success Criteria ✓

- [ ] SC-001: Backend scores reflect transpiled circuit error rates (not source)
- [ ] SC-002: Multi-run aggregation reduces variance ≥30% vs single run
- [ ] SC-003: Fractional gates configs clearly distinguished in results
- [ ] SC-004: ≥95% circuit compatibility across IBM Quantum backends
- [ ] SC-005: Ranking 10 backends completes in <10 seconds
- [ ] SC-006: Backward compatibility maintained (existing code works unchanged)
- [ ] SC-007: Transpilation details transparent in recommendations

### Constitution Principles ✓

- [ ] Principle I: Strong typing (all type hints present, no `Any` except justified)
- [ ] Principle II: Comprehensive testing (≥80% coverage if tests implemented)
- [ ] Principle III: Semantic versioning (MINOR bump, CHANGELOG updated)
- [ ] Principle IV: Code formatting (ruff format passes)
- [ ] Principle V: Documentation (docstrings, user guide, examples)
- [ ] Principle VI: Code simplicity (functions <50 lines, cyclomatic complexity <10)
- [ ] Principle VII: Provider agnostic (BackendV2/Target interfaces only)

---

## Phase Sign-off

**Phase 0 Research**: ✅ **COMPLETE** (research.md created, all APIs validated)  
**Phase 1 Design**: ✅ **COMPLETE** (data-model.md, contracts/, quickstart.md created, agent context updated)  
**Phase 2 Tasks**: ✅ **COMPLETE** (this file)  
**Phase 3 Implementation**: 🔲 **NOT STARTED** (awaiting task execution)  
**Phase 4 Validation**: 🔲 **NOT STARTED** (awaiting implementation)

**Ready for Implementation**: ✅ **YES**  
**Blockers**: None

---

## Next Steps

1. **Start MVP**: Execute Phase 1 (T001-T003) and Phase 2 (T004-T009) to establish foundation
2. **Deliver US1**: Complete Phase 3 (T010-T019) for basic transpiled scoring
3. **Test US1**: Validate end-to-end with examples before proceeding
4. **Extend to US2**: Add multi-run aggregation (Phase 4, T020-T027)
5. **Extend to US3**: Add fractional gates support (Phase 5, T028-T036)
6. **Polish**: Complete documentation and validation (Phase 6, T037-T053)
7. **Release**: Merge to main, update version, deploy

**Recommended Approach**: MVP first (deliver US1 in Week 1), then incremental (US2 in Week 2, US3 in Week 3).

---

*Generated by /speckit.tasks on December 11, 2025*  
*Based on spec.md (3 user stories), plan.md (5 phases), data-model.md (4 entities), contracts/scoring_api.md (6 methods)*
