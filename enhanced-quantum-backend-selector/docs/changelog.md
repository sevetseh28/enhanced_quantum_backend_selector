# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-15

### Added
- Initial release of Enhanced Quantum Backend Selector
- `BackendSelector` class for intelligent backend selection
- Multi-criteria scoring system:
  - Gate fidelity analysis
  - Connectivity matching
  - Coherence time evaluation
  - Queue depth consideration
- `ScoringWeights` dataclass for customizable scoring priorities
- `BackendRecommendation` model with detailed selection information
- Parallel backend analysis using ThreadPoolExecutor (max 10 workers)
- Smart caching with 1-hour TTL for backend metrics
- Support for any Qiskit BackendV2 provider
- Comprehensive type hints (mypy strict mode)
- Full test suite with >80% coverage:
  - Unit tests for all core functionality
  - Integration tests with Aer and fake backends
  - Canonical circuit validation (GHZ, QFT, VQE)
- Complete documentation:
  - User guide with examples
  - API reference
  - Architecture documentation
  - Contributing guidelines
- Example scripts:
  - Basic usage example
  - Advanced usage with custom weights
  - Example validation script
- Development tooling:
  - Pre-commit hooks (ruff, mypy)
  - Poetry dependency management
  - MkDocs documentation site
  - GitHub Actions CI/CD (planned)

### Documentation
- Comprehensive README with quick start
- Getting started guide
- User guide with real-world scenarios
- Examples for common use cases
- Complete API reference
- Architecture and design documentation
- Contributing guide with development setup

[Unreleased]: https://github.com/sevetseh28/enhanced_quantum_backend_selector/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sevetseh28/enhanced_quantum_backend_selector/releases/tag/v0.1.0
