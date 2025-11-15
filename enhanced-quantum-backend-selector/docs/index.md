# Enhanced Quantum Backend Selector

Intelligent quantum backend selection for Qiskit circuits using multi-criteria analysis.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/sevetseh28/enhanced_quantum_backend_selector)
[![Coverage](https://img.shields.io/badge/coverage->80%25-brightgreen.svg)](https://github.com/sevetseh28/enhanced_quantum_backend_selector)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/enhanced-quantum-backend-selector/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

Quantum computing users typically rely on simplistic backend selection methods like `least_busy()`, which only considers queue depth. This library provides intelligent backend selection by analyzing multiple quality factors:

- **Gate Fidelity**: Single-qubit, two-qubit, and readout error rates
- **Connectivity**: Topology match with circuit requirements  
- **Coherence**: T1/T2 times for circuit depth
- **Availability**: Queue depth and operational status

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
```

## Key Features

- ✅ **Multi-Criteria Scoring**: Considers fidelity, connectivity, coherence, and availability
- ✅ **Provider Agnostic**: Works with any Qiskit BackendV2 provider
- ✅ **Customizable Weights**: Adjust scoring priorities for your use case
- ✅ **Smart Caching**: 1-hour TTL cache minimizes backend queries
- ✅ **Parallel Processing**: Scores multiple backends concurrently
- ✅ **Type Safe**: Full mypy strict mode compliance
- ✅ **Well Tested**: >80% code coverage with unit and integration tests

## Why Use This Library?

### The Problem with `least_busy()`

The standard approach in Qiskit:

```python
backend = least_busy(backends)
```

**Only considers queue depth** - ignores gate fidelity, coherence times, connectivity, and other critical quality factors.

### The Enhanced Approach

Our multi-criteria analysis:

```python
selector = BackendSelector(backends)
backend = selector.select_backend(circuit)
```

**Considers all quality factors** with intelligent weighting to find the truly best backend for your specific circuit.

## Installation

```bash
pip install enhanced-quantum-backend-selector
```

Or with Poetry:

```bash
poetry add enhanced-quantum-backend-selector
```

## Next Steps

- [Getting Started Guide](getting-started.md) - Installation and first steps
- [User Guide](user-guide.md) - Detailed usage and configuration
- [Examples](examples.md) - Code examples for common scenarios
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - System design and implementation details

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/sevetseh28/enhanced_quantum_backend_selector/blob/main/LICENSE) file for details.

## Contributing

Contributions are welcome! See our [Contributing Guide](contributing.md) for details.
