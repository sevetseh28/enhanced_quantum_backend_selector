# Target Class Documentation (Qiskit 2.2)

## Overview

The `Target` class is a comprehensive representation of the constraints and capabilities of a quantum backend in Qiskit 2.2. It serves as the single source of truth for what operations a backend supports, where they can be applied, and their performance characteristics.

**Key Purpose**: Enable transpilation and optimization by providing a complete model of backend capabilities including:
- Supported gate set
- Qubit connectivity (coupling map)
- Gate fidelities and error rates
- Gate durations
- Qubit-specific properties

## Location
```python
from qiskit.transpiler import Target, InstructionProperties
```

## Core Concepts

### 1. **Instruction Properties**
Each gate/operation on a backend has properties that vary by qubit(s):
- `duration`: Gate execution time (in dt units or seconds)
- `error`: Gate error rate (0.0 to 1.0)
- `calibration`: Optional pulse-level calibration data

### 2. **Instruction Mapping**
Operations are stored as: `{instruction: {qubits_tuple: properties}}`
- Maps each instruction to specific qubit configurations
- Defines where operations can be applied (connectivity)
- Stores performance metrics per location

### 3. **Global vs Local Properties**
- **Global**: Properties applied to all qubits (e.g., all qubits support H gate)
- **Local**: Qubit-specific properties (e.g., CNOT only on connected pairs)

## Key Attributes

### Target Properties

| Attribute | Type | Description |
|-----------|------|-------------|
| `num_qubits` | int or None | Total number of qubits (None = variable size) |
| `instructions` | list | All supported `Instruction` objects |
| `operations` | list | All supported operation objects (gates, measurements, etc.) |
| `operation_names` | set | String names of all operations |
| `qargs` | dict | Maps operations to valid qubit tuples |
| `dt` | float or None | System timing resolution (duration time unit) |
| `granularity` | int | Minimum time step for pulse schedules |
| `min_length` | int | Minimum pulse schedule length |
| `pulse_alignment` | int | Required alignment for pulse schedules |
| `acquire_alignment` | int | Required alignment for measurements |
| `qubit_properties` | list or None | Per-qubit physical properties (T1, T2, frequency) |

### Qubit Properties

When `qubit_properties` is set, each qubit has:
- `t1`: T1 coherence time (seconds)
- `t2`: T2 coherence time (seconds)  
- `frequency`: Qubit frequency (Hz)

## Key Methods

### Querying Capabilities

```python
# Check if instruction is supported
target.instruction_supported(instruction_name, qargs)

# Get properties for specific instruction on specific qubits
target.get(instruction_name, qargs)

# Get all valid qubit combinations for an operation
target.qargs_for_operation_name(operation_name)

# Get operation names available on specific qubits
target.operation_names_for_qargs(qargs)

# Check if qubits are connected (2-qubit ops allowed)
target.get_qubit_connectivity()
```

### Building Targets

```python
# Add instruction with properties
target.add_instruction(instruction, properties_dict)

# Update existing instruction
target.update_instruction_properties(instruction, qargs, properties)

# Update from another target
target.update_from_instruction_schedule_map(inst_map)
```

### Analysis Methods

```python
# Get coupling map (qubit connectivity graph)
coupling_map = target.build_coupling_map()

# Get all 2-qubit gate names
two_q_gates = [op for op in target.operation_names 
               if any(len(qargs) == 2 for qargs in target.qargs[op])]

# Get operation by name
operation = target.operation_from_name(name)
```

## Important Behavioral Notes

### 1. **None as Universal Support**
If `qargs` for an operation maps to `None`, the operation is supported on **all qubits**:
```python
properties = {None: InstructionProperties(duration=50, error=0.001)}
# This means the gate works on any qubit with these properties
```

### 2. **Variable Qubit Count**
`num_qubits=None` indicates the target supports variable-sized circuits (e.g., simulators)

### 3. **Missing Properties**
If `error` or `duration` is `None`, the property is unknown/not provided

### 4. **Coupling Map Derivation**
The coupling map is **derived** from 2-qubit operations in the target, not stored separately

## Use Cases for Backend Selection

### What Target Tells You:

1. **Gate Set Compatibility**
   - Does backend support all gates in my circuit?
   - Are there native gates that could reduce transpilation overhead?

2. **Connectivity Requirements**
   - Which qubit pairs can interact?
   - How many SWAP gates will be needed?

3. **Performance Characteristics**
   - Which qubits have lowest error rates?
   - Which 2-qubit gates are fastest/most accurate?
   - What are T1/T2 times for coherence analysis?

4. **Transpilation Constraints**
   - What basis gates will transpiler use?
   - Timing constraints for pulse-level optimization

### Critical Metrics for Selection:

```python
# Extract for comparison:
- Average gate error rates by operation type
- Coupling map density/structure
- Qubit coherence times (T1, T2)
- Gate durations
- Supported native gate set overlap with circuit
```

## Example Data Structure

```python
Target(
    num_qubits=5,
    dt=0.222e-9,  # 0.222 nanoseconds
    instructions=[
        ('h', {
            (0,): InstructionProperties(duration=35.5e-9, error=0.00012),
            (1,): InstructionProperties(duration=35.5e-9, error=0.00015),
            # ... for all qubits
        }),
        ('cx', {
            (0, 1): InstructionProperties(duration=256e-9, error=0.0045),
            (1, 2): InstructionProperties(duration=256e-9, error=0.0051),
            # ... only for connected pairs
        }),
        ('measure', {
            (0,): InstructionProperties(duration=1000e-9, error=0.02),
            # ... for all qubits
        })
    ],
    qubit_properties=[
        QubitProperties(t1=120e-6, t2=80e-6, frequency=5.1e9),
        QubitProperties(t1=115e-6, t2=75e-6, frequency=5.2e9),
        # ... for each qubit
    ]
)
```

## Version Notes (Qiskit 2.2)

- `Target` is the **primary** interface in BackendV2 (replaces older configuration objects)
- Fully integrated with transpiler pipeline
- All IBM Quantum backends expose capabilities via Target
- Simulator targets may have `num_qubits=None` for flexibility

## References for Deeper Study

1. Understanding instruction scheduling and timing constraints
2. Pulse-level calibrations and their role in fidelity
3. Transpiler optimization levels and Target usage
4. Custom Target creation for hypothetical backend comparison
