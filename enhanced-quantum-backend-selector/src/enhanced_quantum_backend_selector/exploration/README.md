# Qiskit 2.2 Backend Selection Research Summary

## Overview

This directory contains comprehensive research documentation and examples for understanding `Target` and `BackendV2` classes in Qiskit 2.2. This research is foundational for building an intelligent backend selection system that goes beyond simple `least_busy()` approaches.

## Contents

### 📚 Documentation

1. **[TARGET_CLASS_DOCS.md](./TARGET_CLASS_DOCS.md)**
   - Complete reference for the `Target` class
   - Properties, methods, and data structures
   - Use cases for backend selection
   - Key metrics extraction patterns

2. **[BACKENDV2_DOCS.md](./BACKENDV2_DOCS.md)**
   - BackendV2 interface documentation
   - Relationship between BackendV2 and Target
   - Real hardware vs. simulator differences
   - Best practices for backend analysis

### 🔬 Exploration Scripts

3. **[explore_target.py](./explore_target.py)**
   - Hands-on Target class exploration
   - Creating and querying Target objects
   - Extracting gate properties and connectivity
   - Metrics calculation examples
   - **Run this first** to understand Target internals

4. **[explore_backendv2.py](./explore_backendv2.py)**
   - BackendV2 interface exploration
   - Working with simulators, fake backends, and real IBM hardware
   - Circuit-backend compatibility analysis
   - **Run this second** to see real backend data

5. **[backend_comparison.py](./backend_comparison.py)**
   - Comprehensive backend comparison framework
   - Multi-factor scoring system example
   - Circuit-specific backend ranking
   - **Run this third** for full comparison workflow

6. **[target_class.py](./target_class.py)**
   - Initial Target exploration (starter code)

## Quick Start

### 1. Read the Documentation
```bash
# Start with Target class concepts
cat TARGET_CLASS_DOCS.md

# Then understand BackendV2 interface
cat BACKENDV2_DOCS.md
```

### 2. Run the Exploration Scripts

```bash
# Explore Target class (synthetic backend)
python explore_target.py

# Explore BackendV2 with real/fake backends
python explore_backendv2.py

# See full comparison framework
python backend_comparison.py
```

## Key Insights for Intelligent Backend Selection

### What You Now Know

1. **Target is the Source of Truth**
   - Every backend capability is in `backend.target`
   - Gate errors, durations, connectivity all in one place
   - Qubit properties (T1, T2, frequency) included

2. **Multiple Metrics Matter**
   - Single-qubit gate errors (0.01% - 0.5% typical)
   - Two-qubit gate errors (0.1% - 5% typical)
   - Readout errors (1% - 5% typical)
   - Coherence times (T1: 50-300μs, T2: 40-150μs)
   - Connectivity ratio (1% sparse to 100% full)
   - Queue depth (0-200+ jobs)

3. **Circuit Context is Critical**
   - Shallow circuits → prioritize gate fidelity
   - Deep circuits → prioritize coherence time
   - Many 2Q gates → prioritize connectivity
   - Specific gates → ensure native support

4. **Trade-offs Are Inevitable**
   - Queue time vs. hardware quality
   - Qubit count vs. error rates
   - Transpilation overhead vs. native gates
   - Simulator speed vs. real hardware accuracy

### What Data is Available

From `Target`:
- ✅ Supported operations (gate set)
- ✅ Per-gate, per-qubit error rates
- ✅ Gate durations
- ✅ Coupling map (connectivity)
- ✅ Qubit properties (T1, T2, frequency)
- ✅ Timing constraints (dt, granularity)

From `BackendV2`:
- ✅ Backend name and version
- ✅ Number of qubits
- ✅ Operational status
- ✅ Queue depth
- ✅ Max circuits per job

## Design Patterns for My Selector

### Pattern 1: Metrics Extraction
```python
from backend_comparison import BackendAnalyzer

analyzer = BackendAnalyzer(backend)
metrics = analyzer.extract_metrics()

# metrics contains:
# - avg_1q_error, avg_2q_error, avg_readout_error
# - avg_t1, avg_t2
# - connectivity_ratio, avg_degree
# - pending_jobs
```

### Pattern 2: Circuit-Specific Scoring
```python
score_data = analyzer.score_for_circuit(my_circuit)

# score_data contains:
# - compatible: bool
# - score: float (0-100+)
# - reasons: list of scoring factors
```

### Pattern 3: Multi-Backend Comparison
```python
backends = [backend1, backend2, backend3]
scores = []

for backend in backends:
    analyzer = BackendAnalyzer(backend)
    score = analyzer.score_for_circuit(circuit)
    scores.append((backend, score))

best_backend = max(scores, key=lambda x: x[1]['score'])
```

## Next Steps for My Intelligent Selector

### Phase 1: Core Functionality
- [ ] Define scoring weights (user-customizable)
- [ ] Implement backend caching (metrics change slowly)
- [ ] Add transpilation depth estimation
- [ ] Handle BackendV1 compatibility

### Phase 2: Advanced Features
- [ ] Historical success rate tracking
- [ ] Cost/credit estimation per backend
- [ ] User preference profiles
- [ ] Explain selection reasoning

### Phase 3: Optimization
- [ ] Parallel backend querying
- [ ] Smart metric caching with TTL
- [ ] Batch circuit analysis
- [ ] Fallback strategies

## Important Notes

### Qiskit 2.2 Specifics
- BackendV2 is the **standard** interface (V1 deprecated)
- Target is **comprehensive** (replaces legacy config objects)
- All IBM backends use BackendV2
- Simulators may have `num_qubits=None` (variable size)

### Real Hardware Considerations
- Calibration data updates daily (for IBM backends)
- Queue depth changes constantly
- Some backends may be offline for maintenance
- Error rates are statistical averages

### Simulator Characteristics
- `num_qubits=None` indicates variable circuit size
- No error rates (perfect gates)
- Fully connected (no coupling map constraints)
- Much faster than hardware but not "real"

## Resources

### Qiskit Documentation
- Target class API: `qiskit.transpiler.Target`
- BackendV2 API: `qiskit.providers.BackendV2`
- IBM Quantum backends: `qiskit-ibm-runtime`

### Related Topics
- Transpiler optimization levels
- Pulse-level calibrations
- Noise models
- Error mitigation strategies

## Questions to Consider for My Design

1. **Scoring Algorithm**
   - What weights for different metrics?
   - How to normalize diverse metrics?
   - Linear vs. non-linear scoring?

2. **User Experience**
   - Automatic selection or show top 3?
   - Explain selection reasoning?
   - Allow user to override?

3. **Performance**
   - Cache backend metrics? For how long?
   - Query all backends or filter first?
   - Background updates for queue status?

4. **Edge Cases**
   - No backends meet requirements?
   - Tied scores?
   - Backend goes offline during selection?

5. **Advanced Features**
   - Learn from user's past jobs?
   - Predict transpilation overhead?
   - Consider cost/credits?

---

## Summary

You now have a **complete understanding** of:
- ✅ Target class structure and capabilities
- ✅ BackendV2 interface and usage
- ✅ What metrics are available for selection
- ✅ How to extract and compare backend data
- ✅ Circuit-specific backend scoring patterns

**I'm ready to design my intelligent backend selector!** 🚀

The key insight: **backend selection is multi-dimensional optimization** - no single metric is sufficient. My selector should consider circuit characteristics, backend capabilities, and user preferences to make an intelligent recommendation.

---

*Research completed: November 5, 2025*
*Qiskit version: 2.2 (using BackendV2 interface)*
