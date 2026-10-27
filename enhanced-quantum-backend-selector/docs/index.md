# Enhanced Quantum Backend Selector

Intelligent quantum backend selection for Qiskit circuits using transpilation-based error analysis.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

Quantum computing users typically rely on simplistic backend selection methods like `least_busy()`, which only considers queue depth. This library provides intelligent backend selection by **transpiling your circuit to each backend** and calculating the actual expected error rates.

**Key benefits:**

- **Transpilation-Based**: Circuits are transpiled to each backend's native gate set
- **Real Error Calculation**: Combines the actual gate and readout error rates of the specific qubits the transpiler chose into an estimated success probability
- **Multiple Runs**: Averages over multiple transpilation runs for stability
- **Fractional Gates Support**: Compare standard and fractional-gate versions of a backend (ideal for chemistry circuits)

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
print(f"Expected error: {-best.score_data.score:.2%}")
```

## Installation

```bash
pip install enhanced-quantum-backend-selector
```

Or with Poetry:

```bash
poetry add enhanced-quantum-backend-selector
```

## Key Features

- ✅ **Transpilation-Based Scoring** - Calculates actual error rates for your specific circuit
- ✅ **Fractional Gates Support** - Compare standard and fractional-gate versions of a backend
- ✅ **Provider Agnostic** - Works with any Qiskit BackendV2 provider
- ✅ **Multiple Run Averaging** - Configurable transpilation runs for stable scoring
- ✅ **Parallel Processing** - Scores multiple backends concurrently
- ✅ **Type Safe** - Full mypy strict mode compliance
- ✅ **Well Tested** - >80% code coverage

## Documentation

- [Getting Started](getting-started.md) - Installation and first steps
- [User Guide](user-guide.md) - Detailed usage and configuration
- [Examples](examples.md) - Code examples for common scenarios
- [Benchmarking](benchmarking.md) - Benchmark circuits and methodology
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - System design and implementation details
- [Contributing](contributing.md) - How to contribute
