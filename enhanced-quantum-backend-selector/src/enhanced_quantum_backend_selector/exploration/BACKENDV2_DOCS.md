# BackendV2 Documentation (Qiskit 2.2)

## Overview

`BackendV2` is the abstract base class defining the interface for all quantum backends in Qiskit 2.2. It represents a unified way to interact with both real quantum hardware and simulators, providing a standardized API for accessing backend capabilities and submitting jobs.

**Key Innovation**: BackendV2 uses the `Target` class as its primary capability descriptor, replacing the legacy configuration system from BackendV1.

## Location
```python
from qiskit.providers import BackendV2
from qiskit.providers import Backend  # Generic interface
```

## Core Concepts

### 1. **Target-Centric Design**
- All backend capabilities exposed through a single `Target` object
- Eliminates need for multiple configuration objects
- Provides unified interface for transpilation and optimization

### 2. **Provider Hierarchy**
- Backends belong to Providers (e.g., IBM Quantum, Aer simulators)
- Provider handles authentication and backend discovery
- Backend handles job submission and capability reporting

### 3. **Dynamic Properties**
- Backend properties (errors, durations) can update over time
- Real hardware recalibrated regularly (daily for IBM systems)
- Target should be queried fresh when selecting backends

## Required Abstract Properties

Every BackendV2 implementation must provide:

| Property | Type | Description |
|----------|------|-------------|
| `target` | Target | Complete capability model (gates, connectivity, errors) |
| `max_circuits` | int or None | Maximum circuits per job (None = unlimited) |
| `backend_name` | str | Unique identifier for backend |
| `backend_version` | str | Backend version string |
| `online_date` | datetime | When backend became available |

## Key Properties & Methods

### Essential Properties

```python
backend.target              # Target object with all capabilities
backend.num_qubits         # Total qubits available
backend.coupling_map       # Qubit connectivity (derived from target)
backend.dt                 # Timing resolution (from target)
backend.max_circuits       # Circuits per job limit
backend.operation_names    # Set of supported operation names
```

### Identification

```python
backend.name               # Backend name (e.g., 'ibm_kyoto')
backend.description        # Human-readable description
backend.backend_version    # Version string
backend.provider           # Provider object that owns this backend
```

### Job Submission

```python
# Submit circuits for execution
job = backend.run(circuits, shots=1024, **options)

# Get options schema
options = backend.options
```

### Status & Metadata

```python
# Check if backend is operational (for real hardware)
status = backend.status()
# Returns: BackendStatus(operational, pending_jobs, status_msg)

# Get backend properties (if available)
properties = backend.properties()  # May return None for simulators
```

## BackendV2 vs BackendV1

### Key Differences:

| Aspect | BackendV1 | BackendV2 |
|--------|-----------|-----------|
| Capabilities | Multiple objects (config, properties, defaults) | Single `Target` object |
| Basis Gates | `basis_gates` list | Derived from `target.operations` |
| Coupling Map | Separate `coupling_map` | Derived from `target` 2-qubit ops |
| Gate Properties | In `properties()` | In `target` instruction properties |
| Configuration | `configuration()` method | Properties on `target` |
| Qubit Props | In `properties()` | `target.qubit_properties` |

### Migration Notes:
- Always check backend version: `isinstance(backend, BackendV2)`
- BackendV1 still supported but deprecated path
- All new IBM backends use BackendV2

## Real Hardware Backends

### IBM Quantum Backends

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backend = service.backend('ibm_kyoto')

# BackendV2 properties:
backend.target                    # Full Target with current calibration
backend.num_qubits               # 127 for ibm_kyoto
backend.coupling_map             # Heavy-hex topology
backend.properties()             # Detailed calibration data
backend.status()                 # Queue status
```

### Available Metadata:

1. **Static Information**:
   - Architecture (heavy-hex, linear, etc.)
   - Total qubit count
   - Supported gate set
   - Version and online date

2. **Dynamic Calibration Data** (via `target`):
   - Gate error rates (updated daily)
   - Gate durations
   - Qubit T1, T2 times
   - Readout errors
   - Qubit frequencies

3. **Operational Status**:
   - Online/offline status
   - Pending jobs in queue
   - Estimated wait time

## Simulator Backends

### Local Simulators (Aer)

```python
from qiskit_aer import AerSimulator

# Generic simulator (no noise)
sim = AerSimulator()

# Target properties:
sim.target.num_qubits           # None (variable size)
sim.target.operation_names      # Comprehensive gate set
sim.max_circuits                # High limit or None
```

### Simulator Characteristics:
- `num_qubits = None` allows variable circuit sizes
- Usually support full gate set (no connectivity constraints)
- No error rates or durations (perfect gates)
- Can be configured with noise models

## Use Cases for Backend Selection

### Information Available from BackendV2:

1. **Capability Matching**
   ```python
   # Check if backend supports my circuit's gates
   circuit_ops = set(circuit.count_ops().keys())
   backend_ops = backend.operation_names
   supported = circuit_ops.issubset(backend_ops)
   ```

2. **Connectivity Analysis**
   ```python
   # Get coupling map for layout optimization
   coupling = backend.coupling_map
   # Analyze: is it linear, heavy-hex, fully connected?
   # How many SWAP gates will be needed?
   ```

3. **Performance Metrics**
   ```python
   target = backend.target

   # Average 2-qubit gate error
   cx_errors = [
       target['cx'][(q0, q1)].error
       for (q0, q1) in target.qargs['cx']
       if target['cx'][(q0, q1)].error is not None
   ]
   avg_cx_error = sum(cx_errors) / len(cx_errors)

   # Best qubits (lowest error)
   qubit_readout_errors = [
       target['measure'][(q,)].error
       for q in range(backend.num_qubits)
   ]
   ```

4. **Availability**
   ```python
   # Real-time queue status
   status = backend.status()
   if status.operational and status.pending_jobs < 10:
       # Good time to submit
   ```

5. **Native Gate Analysis**
   ```python
   # Which gates are native (not decomposed)?
   # Native gates = faster + more accurate
   native_gates = backend.target.operation_names

   # Compare with circuit requirements
   # Fewer decompositions = better fidelity
   ```

## Advanced Target Access Patterns

### Circuit-Specific Analysis

```python
def analyze_circuit_requirements(circuit):
    """Extract what circuit needs from backend"""
    return {
        'num_qubits': circuit.num_qubits,
        'depth': circuit.depth(),
        'gate_counts': circuit.count_ops(),
        'two_qubit_gates': count_2q_gates(circuit),
        'required_connectivity': extract_connectivity_pattern(circuit)
    }

def score_backend_for_circuit(backend, circuit_requirements):
    """Score backend compatibility"""
    target = backend.target

    # Check basic requirements
    if backend.num_qubits < circuit_requirements['num_qubits']:
        return 0.0

    # Check gate support
    gates_supported = all(
        gate in target.operation_names
        for gate in circuit_requirements['gate_counts']
    )
    if not gates_supported:
        return 0.0

    # Score based on error rates, connectivity, etc.
    # ... my scoring logic ...
```

### Comparing Backends

```python
def compare_backends(backends, metric='avg_2q_error'):
    """Compare multiple backends on a metric"""
    results = {}

    for backend in backends:
        if metric == 'avg_2q_error':
            target = backend.target
            if 'cx' in target.operation_names:
                errors = [
                    props.error
                    for qargs, props in target['cx'].items()
                    if props.error is not None
                ]
                results[backend.name] = sum(errors) / len(errors) if errors else float('inf')

        elif metric == 'num_qubits':
            results[backend.name] = backend.num_qubits

        elif metric == 'queue_depth':
            status = backend.status()
            results[backend.name] = status.pending_jobs

    return sorted(results.items(), key=lambda x: x[1])
```

## Backend Properties Object (Legacy)

Some backends still provide `properties()` method returning `BackendProperties`:

```python
props = backend.properties()

if props:
    # Access calibration data
    props.t1(qubit)              # T1 time for qubit
    props.t2(qubit)              # T2 time for qubit
    props.frequency(qubit)       # Qubit frequency
    props.gate_error(gate, qubits)      # Gate error rate
    props.gate_length(gate, qubits)     # Gate duration
    props.readout_error(qubit)   # Measurement error
    props.last_update_date       # When calibrated
```

**Note**: In BackendV2, prefer using `target` as it's the primary source. `properties()` may be None for simulators.

## Best Practices for Backend Selection

### 1. **Always Check Backend Version**
```python
from qiskit.providers import BackendV2

if isinstance(backend, BackendV2):
    target = backend.target
else:
    # Handle BackendV1 differently
    pass
```

### 2. **Cache Target for Analysis**
```python
# Target may involve network calls for real backends
target = backend.target  # Fetch once
# Perform multiple analyses on cached target
```

### 3. **Consider Calibration Freshness**
```python
props = backend.properties()
if props and props.last_update_date:
    age = datetime.now() - props.last_update_date
    if age.days > 1:
        # Calibration might be stale
        pass
```

### 4. **Handle Simulators Separately**
```python
if backend.num_qubits is None:
    # Simulator - different selection criteria
    # Focus on speed, noise model, etc.
else:
    # Real hardware - focus on fidelity, connectivity
    pass
```

## Key Insights for Intelligent Selection

### What Makes a Backend "Better"?

1. **Gate Fidelity**: Lower error rates → higher success probability
2. **Connectivity**: Better topology → fewer SWAP gates
3. **Coherence**: Higher T1/T2 → more time before decoherence
4. **Native Gates**: Operations in target → no decomposition overhead
5. **Availability**: Fewer queued jobs → faster results
6. **Qubit Count**: More qubits → handle larger circuits

### Circuit-Dependent Factors:

- **Shallow circuits**: Prioritize gate fidelity over coherence time
- **Deep circuits**: Prioritize coherence time (T1/T2)
- **Many 2-qubit gates**: Prioritize 2-qubit gate quality and connectivity
- **Specific gate requirements**: Ensure native support (e.g., iSWAP, ECR)

### Trade-offs:

- **Queue time** vs **quality**: Fast backend with poorer specs vs slow backend with better specs
- **Qubit count** vs **quality**: More qubits but higher errors vs fewer qubits with lower errors
- **Flexibility** vs **optimization**: Generic basis gates vs specialized native gates

## Version Notes (Qiskit 2.2)

- BackendV2 is the **standard interface** (BackendV1 deprecated)
- All IBM Quantum backends migrated to BackendV2
- Target is comprehensive - no need to check multiple sources
- Backwards compatibility maintained but V2 is preferred

## Example Backend Selection Criteria

```python
criteria = {
    'min_qubits': circuit.num_qubits + 2,  # Some buffer
    'max_avg_2q_error': 0.01,              # 1% max
    'max_readout_error': 0.05,             # 5% max
    'min_t1': 100e-6,                      # 100 μs minimum
    'required_gates': {'cx', 'rz', 'sx'}, # Native gates
    'max_queue_depth': 50,                 # Don't wait too long
    'coupling_connectivity': 'heavy-hex'   # Preferred topology
}
```

## Resources

1. Qiskit documentation on BackendV2 interface
2. IBM Quantum backend specifications
3. Transpiler integration with Target
4. Custom backend creation for testing
