# QAMP Checkpoint 2 - Enhanced Quantum Backend Selector

**Mentee:** Hernan Esteves (@sevetseh28)  
**Mentor:** Junye Huang (@HuangJunye)  
**Project:** Enhanced Quantum Backend Selector  
**Date:** December 18, 2025  
**Word Count:** ~920 words

---

## 🎯 Project Overview

The Enhanced Quantum Backend Selector is a Python library designed to improve how quantum developers select backends for their circuits. Current approaches typically rely on simplistic metrics like `least_busy()`, which only considers queue depth. This library provides intelligent backend selection by transpiling circuits to each available backend and calculating actual expected error based on the specific qubits and gates that will be used.

The core goal is to help quantum developers automatically find the best backend for their specific circuit, considering real performance characteristics rather than generic metrics. This is particularly crucial as quantum hardware diversity increases and circuit-specific optimization becomes more important.

## ✅ Progress Made

I have successfully implemented the core functionality for intelligent backend selection. The library now features:

**Transpilation-Based Scoring System:** The most significant achievement is implementing a realistic scoring methodology. Rather than using weighted multi-criteria scoring with generic backend metrics, the system transpiles each circuit to every backend candidate and calculates the negative sum of all error rates (single-qubit, two-qubit, and readout errors) for the specific qubits that will be used. This provides an accurate, circuit-specific quality metric where higher scores (less negative) indicate lower expected errors.

**Multiple Run Averaging:** To account for transpilation stochasticity, the system runs 3 independent transpilations per backend and averages the scores. This provides stability and reduces sensitivity to unlucky layout selections.

**Fractional Gates Support:** Users can pass both standard and fractional gate versions of the same backend, and the selector will evaluate both configurations independently.

**Performance Optimizations:** Smart caching with 1-hour TTL minimizes expensive backend queries, while parallel processing via ThreadPoolExecutor (up to 10 workers) scores multiple backends concurrently without overwhelming services.

**Code Quality:** The entire codebase maintains mypy strict mode compliance with comprehensive type hints. I achieved 83.09% test coverage with 19/19 tests passing, all examples validated, and both ruff linting and mypy checks passing.

**CI/CD Pipeline:** Implemented automated testing with GitHub Actions running on Python 3.12 and 3.13, automated documentation building and deployment, and comprehensive quality checks on every commit.

**Comprehensive Documentation:** I created extensive documentation including architecture design, user guides, getting started tutorials, API references, and practical examples. All documentation was updated to reflect the transpilation-based scoring approach. MkDocs-based documentation is automatically built and deployed via CI/CD pipeline.

## 🔬 Explorations and Experiments

The development journey involved significant exploration of scoring methodologies:

**Initial Approach - Weighted Multi-Criteria Scoring:** I initially implemented a configurable weighted scoring system with separate factors for gate fidelity, connectivity, coherence times, and queue depth. This included a `ScoringWeights` class allowing users to customize priorities. However, based on domain expert and mentor feedback, I learned that error rates are the criterion that matters most. Factors like qubit connectivity don't need explicit weighting because they are implicitly taken into account once the circuit is transpiled—the transpiler handles layout and SWAP insertion automatically.

**Pivot to Transpilation-Based Scoring:** This insight led me to completely remove the `ScoringWeights` system and implement direct transpilation-based scoring. By transpiling the circuit to each backend, the system reveals exactly which qubits and gates will be used, providing much more accurate error estimation. This approach proved far superior because it calculates errors for the actual execution path rather than generic averages.

**Fractional Gates Support:** I implemented support for fractional gates, which are particularly valuable for QAOA circuits. Since fractional gates are backend-level configuration properties, users must pass both standard and fractional gate versions of the same backend as separate entries in the backends list (e.g., `service.backend('ibm_torino')` and `service.backend('ibm_torino', use_fractional_gates=True)`). The selector treats these as distinct backend configurations and independently evaluates both, allowing direct comparison to determine which configuration yields lower errors for the specific circuit.

## 💡 Key Insights and Learnings

**Transpilation Reveals Ground Truth:** The most important insight is that generic backend metrics are insufficient for quality prediction. Transpilation reveals the actual qubits and gate decompositions that will execute, providing far more accurate error estimates.

**Stochasticity Requires Averaging:** Transpilation produces different layouts on different runs. Single transpilations can give misleading scores; averaging multiple runs provides stable, representative metrics.

**Backend Properties are Context-Dependent:** Fractional gates fundamentally change backend behavior and must be treated as separate backend configurations, not circuit properties.

## 🚧 Technical Challenges

**Accurate Performance Estimation:** The core challenge was determining how to accurately predict circuit performance. With mentor feedback, I overcame this by implementing full transpilation for each backend. While this adds some computational overhead, it remains manageable and provides realistic quality metrics that far outweigh the cost.

**Transpilation Variability:** Initial single-transpilation scoring showed concerning variation between runs. I solved this by averaging three independent transpilations, which significantly stabilized scores.

**Parallel Processing Balance:** Scoring backends in parallel improved performance but required careful thread pool management to avoid overwhelming backend services. ThreadPoolExecutor with a 10-worker limit provided the optimal balance.

**Development Process Complexity:** Using SpecKit for initial development created debugging challenges with convoluted workflows. I resolved this by transitioning to direct GitHub Copilot usage with clear prompts and leveraging mentor feedback on quantum computing best practices and real-world considerations that guided the scoring methodology improvements.

**API Simplification:** The initial `ScoringWeights` API seemed flexible but proved confusing and less accurate than transpilation-based scoring. Removing it entirely simplified the API and improved accuracy simultaneously.

## 📊 Current Status

The project is in excellent shape for completion:

- **Core Functionality:** Complete and working with realistic transpilation-based scoring
- **Test Suite:** 83.09% coverage, all 19 tests passing
- **Code Quality:** mypy strict mode passing, ruff linting clean
- **Documentation:** Comprehensive with 9 documentation pages, all updated for current approach
- **Examples:** 3 validated examples including chemistry circuits with fractional gates
- **CI/CD:** GitHub Actions running tests successfully on Python 3.12 and 3.13

Recent pull request has comprehensive changes ready for review, including the transpilation-based scoring system, fractional gates support, refactored code structure, and updated documentation.

## 🚀 Path Forward to MVP (January 30, 2025)

**Immediate Next Steps:**
- Complete PR review and merge transpilation-based scoring changes
- Finalize CI/CD pipeline for automated PyPI releases
- Set up PyPI trusted publishing configuration

**Pre-Release Phase:**
- Comprehensive integration testing with real IBM backends and simulators
- Benchmarking against standard quantum circuits and use cases:
  - GHZ circuits for entanglement testing
  - Bernstein-Vazirani (all ones) for oracle circuits
  - Mirror circuits (5k gates) for device characterization
  - Chemistry: LUCJ ansatz for molecular simulations
  - QAOA for optimization problems
- Leverage Qiskit benchmarking frameworks ([benchpress](https://github.com/Qiskit/benchpress), [device-benchmarking](https://github.com/qiskit-community/qiskit-device-benchmarking))
- Performance benchmarking and optimization where needed
- Final documentation review and polish
- Create example notebooks and demonstration materials

**Release & Publication:**
- Prepare v0.1.0 release
- Publish package to PyPI
- Deploy documentation to GitHub Pages
- Create demonstration video showing real-world usage

**Post-Release:**
- Gather user feedback and address any critical issues
- Final MVP presentation preparation
