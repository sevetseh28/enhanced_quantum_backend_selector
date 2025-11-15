---
agent: speckit.clarify
---

# Enhanced Quantum Backend Selector - Clarifications

## Purpose

This document captures questions that arise during specification and implementation, along with their authoritative answers. These clarifications refine the specification and guide implementation decisions.

## How to Use This Document

1. **During Specification**: When ambiguities arise, add questions here
2. **During Planning**: Verify design decisions against clarifications
3. **During Implementation**: Reference answers to resolve uncertainties
4. **During Review**: Ensure implementation matches clarified intent

## Clarification Log

### Session 2025-11-15 - Initial Specification

#### Q1: What are the default scoring weights for each criterion?

**Answer**: Balanced priority favoring gate fidelity:
- Gate fidelity: 1.5 (highest priority - circuit success depends most on this)
- Connectivity: 1.0 (important for 2Q gate placement)
- Coherence: 0.8 (affects circuit depth tolerance)
- Queue depth: 0.4 (lowest priority - availability vs quality tradeoff)

**Rationale**: Gate errors are the primary determinant of circuit success. Connectivity affects transpilation overhead. Coherence matters more for deeper circuits. Queue depth is least important for quality.

**Impact**: Default ScoringWeights configuration

---

#### Q2: What caching strategy should be used for backend metrics?

**Answer**: In-memory caching with 1-hour TTL and manual refresh option:
- Cache backend metrics for 1 hour
- Store in memory (not persistent)
- Provide `refresh()` method to force reload
- Cache key: backend name + version

**Rationale**: Backend calibration data changes slowly (typically hourly). In-memory is sufficient for typical usage sessions. Manual refresh allows users to get latest data when needed.

**Impact**: BackendAnalyzer implementation, BackendSelector caching logic

---

#### Q3: How should the system handle cases when all backends are incompatible?

**Answer**: Return empty list with detailed reason:
```python
# When all backends incompatible
recommendations = []  # Empty list
reason = "No backends have sufficient qubits: circuit requires 10, maximum available is 7"
```

**Rationale**: Empty list is Pythonic. Detailed reason helps users understand why and take corrective action (reduce circuit size, get access to larger backends).

**Impact**: BackendSelector.rank_backends() return type, error reporting

---

#### Q4: How should the system handle large backend lists (50+ backends)?

**Answer**: Parallel scoring with ThreadPoolExecutor:
- Use `ThreadPoolExecutor` with `max_workers=10`
- Score backends in parallel
- Combine results and sort
- Target: <5 seconds for 10 backends, <15 seconds for 50 backends

**Rationale**: Backend scoring is I/O bound (querying calibration data). ThreadPoolExecutor is safe for I/O operations. 10 workers balances performance and resource usage.

**Impact**: BackendSelector.rank_backends() implementation, performance requirements

---

#### Q5: How should the system handle missing backend calibration data?

**Answer**: Skip that metric, log warning, continue scoring with available data:
```python
# If T1 times unavailable
score.coherence_score = None  # Exclude from weighted average
logging.warning(f"Backend {backend.name} missing T1 data, coherence score unavailable")
# Continue with remaining metrics
```

**Rationale**: Partial data is better than no recommendation. Users can see data completeness in score breakdown. Allows library to work with backends that have incomplete calibration.

**Impact**: CircuitScorer implementation, BackendRecommendation data model

---

#### Q6: Should the library support historical performance tracking?

**Answer**: No, out of scope for v1.0
- V1 focuses on static backend characteristics only
- Historical tracking requires persistent storage
- Can be added in future version if users request it

**Rationale**: Simplifies v1 implementation. Most value comes from current calibration data. Can reassess based on user feedback.

**Impact**: Explicitly out of scope, documented in specification

---

#### Q7: What happens if a backend doesn't report queue depth?

**Answer**: Treat as zero (best availability):
- Missing queue depth = queue_depth: 0
- Document this assumption
- Log info message

**Rationale**: Conservative assumption. Prevents penalizing backends that don't expose queue info. Users can override with custom weights if this doesn't match their needs.

**Impact**: BackendAnalyzer metrics extraction

---

#### Q8: Should BackendSelector accept backend instances or backend names?

**Answer**: Backend instances (BackendV2 objects):
```python
# Preferred API
selector = BackendSelector(backends=[backend1, backend2])

# NOT supported
selector = BackendSelector(backend_names=["ibm_brisbane", "ibm_kyoto"])
```

**Rationale**:
- Backend instances contain all needed data
- Avoids dependency on specific provider APIs for backend retrieval
- More explicit and type-safe
- Users already have backend objects from provider

**Impact**: BackendSelector constructor signature

---

#### Q9: How detailed should score breakdown be in BackendRecommendation?

**Answer**: Include full CircuitScore data:
```python
@dataclass
class BackendRecommendation:
    backend: BackendV2
    score_data: CircuitScore  # Complete score breakdown
    metrics: BackendMetrics    # Raw backend metrics
    rank: int
```

**Rationale**: Full transparency for debugging and understanding. Users can see exactly why a backend was recommended. Enables custom analysis.

**Impact**: BackendRecommendation data model

---

#### Q10: What format should comparison tables use?

**Answer**: Return structured data, not formatted strings:
```python
# Return List[BackendRecommendation], not formatted table
recommendations = selector.rank_backends(circuit)

# Users can format as needed:
# - Print as table
# - Convert to pandas DataFrame
# - Display in Jupyter notebook
```

**Rationale**: Separation of data and presentation. Users have different output needs (CLI, notebook, web app). Structured data is more flexible.

**Impact**: BackendSelector.compare_backends() return type

---

### Guidelines for Adding Clarifications

When adding new clarifications:

1. **Write Clear Questions**: Specific, unambiguous questions
2. **Provide Complete Answers**: Include code examples when helpful
3. **Explain Rationale**: Why this answer, not alternatives
4. **Document Impact**: Which components/decisions affected
5. **Cross-Reference**: Link to specification sections
6. **Date Sessions**: Group by development session

### Open Questions

*No open questions at this time.*

When questions arise during implementation, add them here with "OPEN" status, then update with answers after discussion.

---

**Last Updated**: 2025-11-15
**Maintained By**: speckit.clarify agent
