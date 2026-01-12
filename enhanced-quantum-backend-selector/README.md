# Enhanced Quantum Backend Selector

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/sevetseh28/enhanced_quantum_backend_selector)
[![Coverage](https://img.shields.io/badge/coverage->80%25-brightgreen.svg)](https://github.com/sevetseh28/enhanced_quantum_backend_selector)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/enhanced-quantum-backend-selector/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Intelligent quantum backend selection for Qiskit circuits using transpilation-based error analysis.

## Overview

Quantum computing users typically rely on simplistic backend selection methods like `least_busy()`, which only considers queue depth. This library provides intelligent backend selection by **transpiling your circuit to each backend** and calculating the actual expected error rates:

- **Transpilation-Based**: Circuits are transpiled to each backend's native gate set
- **Real Error Calculation**: Sums actual error rates for the specific qubits and gates used
- **Multiple Runs**: Averages over multiple transpilation runs for stability (default: 3, configurable)
- **Direct Quality Metric**: Score = negative total error (higher is better)

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
print(f"Score: {best.score_data.score:.3f}")  # Negative error sum
print(f"Expected error: {-best.score_data.score:.2%}")  # As percentage
print(f"Reasons: {', '.join(best.score_data.reasons)}")
```

## Features

- ✅ **Transpilation-Based Scoring**: Calculates actual error rates for your specific circuit
- ✅ **Fractional Gates Support**: Automatically evaluates with/without fractional gates for chemistry circuits
- ✅ **Provider Agnostic**: Works with any Qiskit BackendV2 provider (IBM, Aer, etc.)
- ✅ **Multiple Run Averaging**: Configurable transpilation runs (default: 3) for stable scoring
- ✅ **Smart Caching**: 1-hour TTL cache minimizes backend queries
- ✅ **Parallel Processing**: Scores multiple backends concurrently (up to 10 workers)
- ✅ **Comprehensive Type Hints**: Full mypy strict mode compliance
- ✅ **Extensive Documentation**: Detailed docstrings with examples

## Rank All Backends

```python
# Get full ranking
rankings = selector.rank_backends(qc, top_n=5)

for rec in rankings:
    error_pct = -rec.score_data.score * 100
    print(f"#{rec.rank}. {rec.backend.name}: {rec.score_data.score:.4f} ({error_pct:.2f}% error)")
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

## Benchmarking

The library includes a comprehensive benchmarking suite with real-world quantum circuits to evaluate backend selector performance using mock backends that simulate real IBM Quantum processors (Heron R1, Heron R2, Heron R3, and Nighthawk):

```bash
# Run full benchmark suite
poetry run python benchmarks/run_benchmarks.py

# Run example benchmarks
poetry run python examples/run_benchmarks.py

# Run benchmark tests
poetry run pytest tests/test_benchmarks.py -v
```

**Benchmark Circuits:**
- **GHZ**: Multi-qubit entanglement testing
- **Bernstein-Vazirani**: Parallel operations and phase kickback
- **Mirror_5k**: Device benchmarking (circuit inversion)
- **LUCJ Ansatz**: Quantum chemistry applications
- **QAOA**: Combinatorial optimization

**Mock Backends** (based on real IBM processors):
- **IBM Heron R1**: 133 qubits, heavy-hex topology, 1,800 gate capacity
- **IBM Heron R2**: 156 qubits, heavy-hex topology, 5,000 gate capacity
- **IBM Heron R3**: 156 qubits, heavy-hex topology, improved error rates
- **IBM Nighthawk**: 120 qubits, square lattice, superior connectivity

See [Benchmarking Guide](docs/benchmarking.md) for detailed methodology, metrics, and references.

## Documentation

- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Benchmarking Guide](docs/benchmarking.md)
- [Examples](examples/)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Release Process](RELEASE.md)
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
