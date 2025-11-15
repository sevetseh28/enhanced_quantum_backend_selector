---
agent: speckit.specify
---

# Enhanced Quantum Backend Selector - Specification

## Problem Statement

Quantum computing users currently rely on simplistic backend selection methods, primarily `least_busy()`, which only considers queue depth. This approach ignores critical factors that significantly impact circuit execution success such as gate error rates, qubit connectivity topology, coherence times, native gate set compatibility, and circuit-specific requirements.

## Solution

An intelligent backend selector that performs multi-dimensional analysis to recommend the optimal quantum backend for a given circuit, considering hardware characteristics, circuit requirements, and runtime availability.

## Core Capabilities

### 1. Circuit Analysis
Extract requirements from quantum circuits:
- Qubit count requirements
- Gate type requirements
- Circuit depth analysis
- Two-qubit gate count and connectivity patterns

### 2. Backend Metrics Extraction
Gather comprehensive data from quantum backends:
- Gate error rates (1Q, 2Q, readout)
- Qubit coherence times (T1, T2)
- Connectivity topology (coupling map)
- Native gate set
- Queue status and availability
- Operational status

### 3. Multi-Criteria Scoring
Evaluate backends against circuit requirements using:
- **Compatibility:** Qubit count and gate set support
- **Fidelity:** Gate and readout error rates (weight: 1.5 - highest priority)
- **Connectivity:** Topology match with circuit needs (weight: 1.0)
- **Coherence:** T1/T2 times for circuit depth (weight: 0.8)
- **Availability:** Queue depth and operational status (weight: 0.4)

Default weights prioritize gate fidelity while balancing other quality factors. Weights are user-customizable.

### 4. Recommendation & Reasoning
Provide clear, actionable recommendations:
- Ranked list of suitable backends
- Score breakdown by criteria
- Human-readable explanations
- Incompatibility warnings

### 5. Provider Agnostic Design
Work with any Qiskit BackendV2 provider:
- IBM Quantum backends
- Qiskit Aer simulators
- Future providers (when BackendV2 compatible)

## Design Principles

1. **Target-Centric:** All backend analysis through Qiskit's `Target` class
2. **Extensible:** Easy to add new scoring criteria
3. **Transparent:** Clear reasoning for recommendations
4. **Flexible:** User-customizable weights and criteria
5. **Efficient:** Cached metrics to minimize backend queries (1-hour TTL, in-memory, with manual refresh option)
6. **Robust:** Gracefully handle missing calibration data (skip metric, log warning, continue with available data)
7. **Scalable:** Parallel backend scoring using ThreadPoolExecutor (max_workers=10) for large backend lists

## User Experience

**Input:**
- Quantum circuit (Qiskit `QuantumCircuit`)
- List of available backends
- Optional: Custom scoring weights

**Output:**
- Ranked backend recommendations
- Compatibility status
- Score breakdown with explanations

## Error Handling & Edge Cases

**Incompatible Backends:**
- When all backends are incompatible with the circuit, return empty list with detailed reason property explaining why (e.g., "No backends have sufficient qubits: circuit requires 10, maximum available is 7")

**Missing Calibration Data:**
- Skip metrics that are unavailable for a backend
- Log warning indicating which metrics are missing
- Continue scoring with available data
- Include data completeness information in recommendation

**Network/API Failures:**
- Handle backend status query failures gracefully
- Use cached data when fresh data unavailable
- Provide degraded recommendations with warnings when necessary

## Success Criteria

1. Recommends backends that produce better results than `least_busy()`
2. Handles all BackendV2-compatible providers
3. Analysis completes in <5 seconds for 10 backends, scalable to 50+ backends with parallel processing
4. Clear, actionable recommendations with detailed reasoning
5. Clean separation of concerns
6. Graceful handling of incompatible backends (returns empty list with explanation)
7. Robust handling of missing/incomplete calibration data (continues with available metrics)
8. Validated against canonical quantum circuits (GHZ, QFT, VQE ansätze) showing measurably better fidelity than `least_busy()` baseline

## Out of Scope (Initial Version)

- Historical success rate tracking
- Cost/credit optimization
- Automatic circuit transpilation
- Real-time backend monitoring
- User preference learning

## Validation & Testing Strategy

### Canonical Quantum Circuits

To validate recommendation quality, the library MUST include canonical quantum circuits as test cases:

**Purpose:**
- Verify that recommended backends produce better fidelity than `least_busy()` baseline
- Provide reproducible benchmarks for different circuit types
- Enable regression testing of recommendation algorithm improvements

**Canonical Circuit Suite:**

1. **GHZ States (Greenberger-Horne-Zeilinger)**
   - Tests: Multi-qubit entanglement, long-range connectivity
   - Variations: 3-qubit, 5-qubit, 10-qubit GHZ
   - Success metric: State fidelity to ideal GHZ state

2. **QFT (Quantum Fourier Transform)**
   - Tests: Circuit depth handling, coherence time requirements
   - Variations: 4-qubit, 8-qubit QFT
   - Success metric: Output distribution fidelity

3. **VQE Ansätze (Variational Quantum Eigensolver)**
   - Tests: Gate set compatibility, connectivity patterns
   - Variations: UCCSD ansatz, Hardware-efficient ansatz
   - Success metric: Expectation value accuracy

4. **Random Circuit Sampling**
   - Tests: General-purpose circuit handling
   - Variations: Different depths and qubit counts
   - Success metric: Heavy output generation probability

**Validation Methodology:**
- For each canonical circuit, compare recommendations from `BackendSelector` vs `least_busy()`
- Execute circuits on both recommended backends (if available)
- Measure and compare: state fidelity, expectation values, or success probability
- Document improvement margin (e.g., "15% better fidelity on GHZ-5")

**Integration:**
- Canonical circuits stored in `tests/fixtures/canonical_circuits.py`
- Validation tests in `tests/test_canonical_validation.py`
- CI/CD runs validation on fake backends (deterministic)
- Optional extended validation against real IBM backends (requires credentials, not in CI)

## Clarifications

### Session 2025-11-15

- Q: What are the default scoring weights for each criterion? → A: Balanced priority (fidelity=1.5, connectivity=1.0, coherence=0.8, queue=0.4)
- Q: What caching strategy should be used for backend metrics? → A: 1-hour TTL, in-memory, with manual refresh method
- Q: How should the system handle cases when all backends are incompatible? → A: Return empty list with detailed reason property
- Q: How should the system handle large backend lists (50+ backends)? → A: Parallel scoring with ThreadPoolExecutor, max_workers=10
- Q: How should the system handle missing backend calibration data? → A: Skip that metric, log warning, continue scoring with available data
