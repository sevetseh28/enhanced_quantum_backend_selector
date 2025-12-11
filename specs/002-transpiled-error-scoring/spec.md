# Feature Specification: Transpiled Circuit Error-Based Scoring

**Feature Branch**: `002-transpiled-error-scoring`
**Created**: December 11, 2025
**Status**: Draft
**Input**: User description: "Requirements have changed. For scoring mechanism we need to use the transpiled circuit to core, not the source one. We also only care about error rates, we need to sum up all the error rates of the instructions used based on the qubit used. The transpiler is stochastic, so for scoring we should transpile e.g. 3 times. We don't care about qubit count. We also need to consider that when getting a backend there's a flag to get it with fractional gates True or False, we need to consider both too."

## Clarifications

### Session 2025-12-11

- Q: When aggregating error scores from multiple transpilation runs, which statistical measure should be used by default? → A: Mean (average)
- Q: Should the system automatically evaluate both fractional gate configurations (enabled and disabled) for every backend, or should this be a user-configurable option? → A: User-configurable with "both" as default
- Q: When all transpilation runs fail for a backend, how should the system handle backend ranking? → A: Exclude from ranking with detailed reason
- Q: How should the system handle caching of transpiled circuits given that transpilation is stochastic and runs multiple times per backend? → A: Cache backend calibration data only
- Q: When a circuit requires more qubits than a backend provides, should the system attempt to score the backend anyway or immediately exclude it? → A: Attempt scoring anyway (regardless of the qubit count the circuit should compile)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accurate Backend Scoring with Transpiled Circuits (Priority: P1)

As a quantum algorithm developer, I need the backend selector to score backends based on the actual transpiled circuit that will run on the hardware, not my source circuit, so that I get accurate error rate predictions for my specific workload.

**Why this priority**: This is the core value proposition of the updated feature - providing realistic error estimates based on what actually runs on quantum hardware. Without transpilation, error estimates are unrealistic and misleading since the source circuit differs significantly from what executes.

**Independent Test**: Can be fully tested by providing a source circuit, transpiling it against a specific backend, extracting error rates for each instruction on each qubit, summing them, and comparing the result against the backend's score. This delivers immediate value: realistic error predictions.

**Acceptance Scenarios**:

1. **Given** a quantum circuit and a backend, **When** the backend is scored, **Then** the circuit is transpiled to that backend's native gate set and the error calculation uses the transpiled circuit instructions
2. **Given** a transpiled circuit with specific gate instructions on specific qubits, **When** error rates are calculated, **Then** the system retrieves the error rate for each instruction-qubit pair from the backend's calibration data and sums them
3. **Given** a backend with missing error rate data for certain instruction-qubit pairs, **When** error calculation occurs, **Then** those missing values are handled gracefully (skipped with a warning) and scoring continues with available data
4. **Given** two identical source circuits transpiled to different backends, **When** both backends are scored, **Then** each backend's score reflects its specific transpiled circuit and native error rates

---

### User Story 2 - Stochastic Transpilation Handling (Priority: P2)

As a quantum researcher, I need the scoring system to account for transpilation variability by running multiple transpilation passes, so that I get a representative average score rather than a potentially lucky or unlucky single transpilation result.

**Why this priority**: Quantum circuit transpilation is non-deterministic - the same circuit can transpile differently each time. A single transpilation could produce an unusually good or bad result, misleading the backend selection. Multiple runs provide statistical confidence.

**Independent Test**: Can be tested by transpiling the same circuit multiple times (e.g., 3 times) to the same backend, calculating separate error scores for each transpilation, and verifying that the final score is derived from these multiple samples (e.g., average or median). This delivers value by reducing selection variance.

**Acceptance Scenarios**:

1. **Given** a circuit and a backend, **When** scoring is performed, **Then** the circuit is transpiled multiple times (configurable, default 3) to the same backend
2. **Given** multiple transpilation results for the same circuit-backend pair, **When** calculating the final score, **Then** error rates from all transpilation runs are aggregated using the mean (average) by default, with median and minimum available as configurable alternatives
3. **Given** one transpilation run fails unexpectedly, **When** other runs succeed, **Then** the system uses the successful runs and logs a warning about the failure
4. **Given** a user-specified number of transpilation runs, **When** scoring occurs, **Then** exactly that many transpilation attempts are made per backend

---

### User Story 3 - Fractional Gates Configuration Support (Priority: P2)

As a quantum circuit designer, I need the backend selector to consider both fractional gates enabled and disabled configurations when retrieving backend targets, so that I can evaluate backends under different operational modes and choose the best option for my circuit's requirements.

**Why this priority**: Different fractional gate settings can significantly impact circuit transpilation and error rates. Some circuits benefit from fractional gates while others perform better with discrete gates. Supporting both configurations ensures comprehensive backend evaluation.

**Independent Test**: Can be tested by retrieving a backend's target with fractional gates enabled vs disabled, transpiling the same circuit under both configurations, and verifying that separate scores are calculated for each configuration. This delivers value by revealing which operational mode produces better results for a specific circuit.

**Acceptance Scenarios**:

1. **Given** a backend that supports fractional gates, **When** scoring is performed with default settings, **Then** the backend is evaluated with both fractional gates enabled (True) and disabled (False)
2. **Given** a user specifies a single fractional gates configuration preference, **When** scoring is performed, **Then** only that configuration is evaluated for performance optimization
3. **Given** backend target retrieved with fractional gates flag set, **When** transpilation occurs, **Then** the transpiler respects the fractional gates configuration from the target
4. **Given** scores calculated for multiple fractional gate configurations, **When** presenting results, **Then** the system clearly indicates which configuration produced each score
5. **Given** a backend that doesn't support fractional gates, **When** scoring occurs, **Then** only the available configuration is evaluated without errors

---

### Edge Cases

- What happens when a backend's target has incomplete calibration data for the transpiled instructions?
  - System skips missing instruction-qubit error rates, logs warnings, and scores based on available data
  
- How does the system handle transpilation failures?
  - If a single transpilation run fails: log warning, continue with successful runs
  - If all transpilation runs fail for a backend: exclude backend from ranking results and provide detailed failure reason in logs and error reporting
  
- What if a circuit transpiles to zero instructions (e.g., identity circuit)?
  - Assign a baseline score (perfect score since no errors can occur)
  
- How are tie-breaking scenarios handled when backends have identical aggregated error rates?
  - Secondary sorting by backend name (alphabetical) for deterministic ordering
  
- What happens when the number of transpilation runs is set to 0 or negative?
  - Validation error raised with clear message requiring positive integer
  
- How does the system handle backends with no coupling map (fully connected)?
  - Transpiler handles fully connected topology naturally; all qubit pairs valid

- What happens when a circuit appears to require more qubits than a backend provides?
  - System attempts transpilation regardless of apparent qubit count mismatch, letting the transpiler determine actual compatibility (circuit optimization may reduce qubit requirements)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST transpile the user's source circuit to each backend's native gate set before calculating error-based scores
- **FR-002**: System MUST calculate backend scores by summing the error rates of all instructions in the transpiled circuit, where each instruction's error rate is specific to the qubits it operates on
- **FR-003**: System MUST retrieve instruction error rates from the backend's target calibration data, matching instruction type and qubit indices
- **FR-004**: System MUST perform multiple independent transpilation runs per backend (configurable count, default 3) to account for stochastic transpilation behavior
- **FR-005**: System MUST aggregate error scores from multiple transpilation runs using mean (average) by default, with median and minimum available as user-configurable alternatives
- **FR-006**: System MUST provide user-configurable fractional gates evaluation mode with three options: both configurations (default), enabled only, or disabled only
- **FR-007**: System MUST evaluate backends with both fractional gates enabled (True) and disabled (False) by default when the backend supports fractional gates
- **FR-008**: System MUST distinguish between scores from different fractional gate configurations in the results
- **FR-009**: System MUST handle missing error rate data gracefully by skipping unavailable instruction-qubit pairs and logging warnings
- **FR-010**: System MUST provide configurable transpilation run count (positive integer, validated at input)
- **FR-011**: System MUST report which transpilation runs succeeded and which failed for transparency
- **FR-012**: System MUST exclude backends from ranking results when all transpilation runs fail, providing detailed failure reasons in error reporting and logs
- **FR-013**: System MUST cache backend calibration data (error rates, target properties) but NOT cache transpiled circuits, ensuring fresh transpilations for each scoring operation to respect stochastic behavior
- **FR-014**: System MUST attempt to transpile and score all backends regardless of apparent qubit count requirements, allowing the transpiler to determine actual compatibility through circuit optimization
- **FR-015**: System MUST eliminate qubit count as a scoring factor (compatibility check remains, but not weighted in score)
- **FR-016**: System MUST preserve backward compatibility by maintaining the same public API surface (method signatures unchanged)
- **FR-017**: System MUST continue to use the existing scoring weight system for any remaining criteria (if applicable) while prioritizing error rate sums
- **FR-018**: System MUST handle circuits that transpile to zero instructions (identity circuits) by assigning a perfect error score (0.0)
- **FR-019**: System MUST provide deterministic backend ranking by using secondary sort criteria (e.g., backend name) when error scores are identical

### Key Entities

- **TranspiledCircuit**: Represents a circuit after transpilation to a specific backend, containing native instructions with qubit assignments
- **InstructionErrorRate**: Maps an instruction type, qubit indices, and error rate value retrieved from backend calibration data
- **TranspilationRun**: Captures a single transpilation attempt including the resulting circuit, success/failure status, and calculated error sum
- **ScoringConfiguration**: Encapsulates user-configurable parameters including transpilation run count, aggregation method (mean/median/min), and fractional gates evaluation mode
- **BackendConfiguration**: Represents a specific backend target configuration with fractional gates enabled or disabled
- **AggregatedScore**: Contains the final score derived from multiple transpilation runs, including individual run scores, aggregation method used, and statistical metadata (e.g., variance)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend scores reflect actual hardware error rates by calculating error sums from transpiled circuits rather than source circuits
- **SC-002**: Scoring accuracy is improved by averaging error rates across multiple transpilation runs (default 3), reducing selection variance by at least 30% compared to single-run transpilation
- **SC-003**: Users can evaluate backends under different operational modes by comparing scores from fractional gates enabled vs disabled configurations, with clear indication of which configuration produced each score
- **SC-004**: System handles at least 95% of real-world circuits without transpilation failures across major IBM Quantum backends
- **SC-005**: Backend ranking completes within 10 seconds for 10 backends when evaluating multiple transpilation attempts and fractional gate configurations
- **SC-006**: All public API methods maintain backward compatibility with existing user code (no breaking changes to method signatures)
- **SC-007**: System provides transparent scoring details including individual transpilation run results and aggregation method used in recommendations

## Assumptions

- The Qiskit transpiler API remains stable and supports retrieving backend targets with fractional gates flags
- Backend calibration data includes per-qubit error rates for supported instructions (standard in IBM Quantum backends)
- Transpilation stochasticity is significant enough to warrant multiple runs (industry-standard practice in quantum computing)
- Three transpilation runs provide sufficient statistical confidence for most use cases (configurable for power users)
- Mean (average) aggregation provides the most balanced and interpretable default measure for users, with median and minimum available for specific use cases requiring outlier robustness or conservative estimates
- Fractional gates settings significantly impact circuit quality for a meaningful subset of circuits
- Users prefer comprehensive backend evaluation (both fractional gate configs) by default, but value the ability to optimize performance by selecting a single configuration when their preference is known
- Backend calibration data changes slowly enough that existing 1-hour TTL caching remains appropriate, while transpiled circuits must be regenerated each scoring run to capture stochastic variation
- Transpilation performance is fast enough that re-transpiling circuits each run does not significantly impact overall scoring time compared to backend API latency
- The Qiskit transpiler can optimize circuits to fit backends through techniques like gate cancellation and circuit simplification, potentially reducing apparent qubit requirements
