# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Transpiled Circuit Error-Based Scoring**: Backend selection now uses actual transpiled circuits instead of source circuits for realistic error predictions
  - `_transpile_circuit()`: Transpiles circuit to backend's native gate set
  - `_calculate_error_sum()`: Sums instruction-specific error rates from backend calibration data
  - Multiple transpilation runs per backend (default 3) to account for stochastic behavior
- **New Data Models**:
  - `TranspilationRun`: Captures individual transpilation results with error sums
  - `AggregatedScore`: Aggregates multiple runs with statistical measures (mean/median/minimum)
  - `ScoringConfiguration`: User-configurable transpilation parameters
- **Aggregation Methods**: Choose between mean (default), median, or minimum for combining multiple transpilation runs
- **Fractional Gates Support**: Placeholder for evaluating backends with different fractional gate configurations
- **Enhanced BackendRecommendation**: Added `transpilation_details` and `fractional_gates_used` optional fields
- **Smart Caching**: 1-hour TTL cache for backend calibration data (transpilations always fresh)
- **Parallel Transpilation**: Uses ThreadPoolExecutor for faster scoring

### Changed
- **Breaking (Minor)**: `select_backend()` and `rank_backends()` now accept optional `config` parameter for transpilation configuration
- **Deprecated**: Passing `weights` directly to selection methods (use `config.weights` instead)
- **Scoring Algorithm**: Switched from static backend metrics to transpiled circuit error sums
- **Backend Exclusion**: Backends that fail all transpilations are automatically excluded from rankings
- **Error Handling**: Improved logging for transpilation failures and missing error data

### Fixed
- Identity circuits (zero instructions) now correctly receive perfect score (0.0 error sum)
- Missing error rate data is now handled gracefully with warnings

## [0.1.0] - TBD

### Added
- BackendSelector class for intelligent quantum backend selection
- Multi-criteria scoring system (fidelity, connectivity, coherence, availability)
- Support for any Qiskit BackendV2 provider
- Comprehensive test suite with >80% coverage
- Canonical quantum circuits for validation (GHZ, QFT, VQE, random)
- Complete documentation with examples
- CI/CD pipelines for testing, documentation, and PyPI publishing

[Unreleased]: https://github.com/sevetseh28/enhanced_quantum_backend_selector/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sevetseh28/enhanced_quantum_backend_selector/releases/tag/v0.1.0
