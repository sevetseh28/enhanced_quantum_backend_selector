# Enhanced Quantum Backend Selector

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/sevetseh28/enhanced_quantum_backend_selector)
[![Coverage](https://img.shields.io/badge/coverage->80%25-brightgreen.svg)](https://github.com/sevetseh28/enhanced_quantum_backend_selector)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/enhanced-quantum-backend-selector/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Intelligent quantum backend selection for Qiskit circuits using multi-criteria analysis.

## Overview

Quantum computing users typically rely on simplistic backend selection methods like `least_busy()`, which only considers queue depth. This library provides intelligent backend selection by analyzing multiple quality factors:

- **Gate Fidelity**: Single-qubit, two-qubit, and readout error rates
- **Connectivity**: Topology match with circuit requirements
- **Coherence**: T1/T2 times for circuit depth
- **Availability**: Queue depth and operational status

## Installation

```bash
pip install enhanced-quantum-backend-selector
```

Or with Poetry:

```bash
poetry add enhanced-quantum-backend-selector
```

## Quick Start

```python
from enhanced_quantum_backend_selector import BackendSelector
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService

# Get available backends
service = QiskitRuntimeService()
backends = service.backends()

# Create your circuit
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

# Select the best backend
selector = BackendSelector(backends)
best = selector.select_backend(qc)

print(f"Recommended: {best.backend.name}")
print(f"Score: {best.score_data.score:.2f}")

# View transpilation details
if best.transpilation_details:
    print(f"Error sum: {best.transpilation_details.final_score:.6f}")
    print(f"Successful runs: {best.transpilation_details.successful_runs}")
```

## Features

- ✅ **Multi-Criteria Scoring**: Considers fidelity, connectivity, coherence, and availability
- ✅ **Transpiled Circuit Scoring**: Uses actual transpiled circuits for realistic error predictions
- ✅ **Stochastic Transpilation Handling**: Runs multiple transpilations and aggregates results
- ✅ **Provider Agnostic**: Works with any Qiskit BackendV2 provider (IBM, Aer, etc.)
- ✅ **Customizable Configuration**: Control transpilation runs, aggregation method, optimization level
- ✅ **Smart Caching**: 1-hour TTL cache for backend calibration data
- ✅ **Parallel Processing**: Scores multiple backends concurrently (up to 10 workers)
- ✅ **Comprehensive Type Hints**: Full mypy strict mode compliance
- ✅ **Extensive Documentation**: Detailed docstrings with examples

## Transpilation Configuration

```python
from enhanced_quantum_backend_selector import ScoringConfiguration

# Custom transpilation configuration
config = ScoringConfiguration(
    transpilation_runs=5,          # Run 5 times instead of default 3
    aggregation_method='median',   # Use median instead of mean
    optimization_level=2           # Lower optimization level
)

best = selector.select_backend(qc, config=config)
```

## Custom Scoring Weights

```python
from enhanced_quantum_backend_selector import ScoringWeights

# Prioritize fast execution over quality
fast_weights = ScoringWeights(
    gate_fidelity_weight=1.0,
    connectivity_weight=0.8,
    coherence_weight=0.6,
    queue_weight=2.0  # Much higher weight
)

best = selector.select_backend(qc, weights=fast_weights)
```

## Rank All Backends

```python
# Get full ranking
rankings = selector.rank_backends(qc)

for rec in rankings[:5]:
    print(f"{rec.rank}. {rec.backend.name}: {rec.score_data.score:.2f}")
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

```bash
# Clone repository
git clone https://github.com/sevetseh28/enhanced_quantum_backend_selector.git
cd enhanced-quantum-backend-selector/enhanced-quantum-backend-selector

# Install with development dependencies
poetry install --with dev,docs

# Run tests
poetry run pytest

# Run type checking
poetry run mypy src/

# Format code
poetry run ruff format .
```

## Documentation

- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Examples](examples/)
- [Changelog](CHANGELOG.md)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{enhanced_quantum_backend_selector,
  title = {Enhanced Quantum Backend Selector},
  author = {sevetseh28},
  year = {2025},
  url = {https://github.com/sevetseh28/enhanced_quantum_backend_selector}
}
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.
