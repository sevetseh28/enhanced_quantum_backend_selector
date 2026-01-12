# Benchmark Summary

This document summarizes the benchmark results from the Enhanced Quantum Backend Selector test suite, demonstrating how different quantum circuits favor different backend generations based on their characteristics.

## Backends Under Test

| Backend | Processor | Qubits | Topology | Notes |
|---------|-----------|--------|----------|-------|
| FakeTorino | Heron R1 | 133 | Heavy-hex | First generation Heron |
| FakeMarrakesh | Heron R2 | 156 | Heavy-hex | Second generation Heron |
| FakeFez | Heron R3 | 156 | Heavy-hex | Latest generation, best error rates |
| FakeNighthawk | Nighthawk | 120 | Square lattice | Different architecture, 2D grid connectivity |

## Benchmark Results

### Winners by Circuit Type

| Circuit | Winner | Runner-up | Key Factor |
|---------|--------|-----------|------------|
| **ShallowWide-130q** | **Heron R3** | Heron R2 | Qubit count >120 excludes Nighthawk |
| **GHZ-127** | **Heron R3** | Heron R2 | Qubit count >120 excludes Nighthawk |
| **DeepLinear-20q-d30** | **Heron R2** | Nighthawk | Better qubit calibration for mapped region |
| **Mirror-5q** | **Nighthawk** | Heron R2 | Lower accumulated errors over ~670 gates |
| **Ising2D-5x5** | **Nighthawk** | Heron R2 | Native square lattice topology |
| **QVstyle-16q-d10** | **Nighthawk** | Heron R2 | Square topology handles random patterns |
| **LUCJ-Chemistry-52q** | **Nighthawk** | Heron R3 | Better connectivity for this circuit size |
| **GHZ-10** | **Nighthawk** | Heron R2 | Best calibrated qubits for small circuits |
| **BernsteinVazirani-10** | **Nighthawk** | Heron R3 | Best calibrated qubits for small circuits |
| **QAOA-Ring-12q** | **Nighthawk** | Heron R2 | Ring connectivity maps well to square |

## Key Trade-offs Demonstrated

### 1. Qubit Count vs. Availability

**Finding**: Circuits requiring >120 qubits automatically exclude Nighthawk (120q limit).

- **ShallowWide-130q**: Only Heron R2/R3 (156q) can run this circuit
- **GHZ-127**: Same constraint applies
- **Winner**: Heron R3 with best error rates among high-qubit backends

**Implication**: For large-scale quantum algorithms, Heron family is the only option.

### 2. Topology Matching

**Finding**: 2D grid algorithms naturally favor square lattice topology.

- **Ising2D circuits**: Nighthawk's square lattice requires no SWAP gates for grid interactions
- **Heavy-hex (Heron)**: Requires additional routing for 2D nearest-neighbor patterns

**Implication**: Algorithm-hardware co-design matters—choose topology that matches your problem structure.

### 3. Calibration Snapshot Effects

**Finding**: Same-generation backends can have different performance based on which physical qubits get mapped.

- The transpiler selects different qubit regions on each backend
- FakeFez (R3) has better *average* error rates but may lose to R2 for specific circuits
- The selector correctly evaluates *actual mapped qubits*, not device averages

**Implication**: Real-time calibration data is crucial; don't assume newer = always better.

### 4. Circuit Depth vs. Error Accumulation

**Finding**: Deep circuits amplify error rate differences.

- **DeepLinear-20q-d30** (1780 gates): Small error differences compound over many layers
- **Shallow circuits** (GHZ-10, QAOA): Error differences less pronounced

**Implication**: For deep circuits, prioritize backends with lowest gate error rates.

### 5. Connectivity Requirements

**Finding**: Circuit connectivity patterns affect routing overhead.

- **Linear chains** (GHZ, LUCJ): Map well to both topologies
- **2D grids** (Ising2D): Favor square lattice
- **Random patterns** (QV-style): Square lattice provides more uniform connectivity

## Circuit Descriptions

### Baseline Circuits
- **GHZ-N**: Greenberger-Horne-Zeilinger state with linear entanglement chain
- **BernsteinVazirani-N**: Oracle-based algorithm testing phase kickback

### Physics Simulation
- **Ising2D-RxC**: 2D transverse-field Ising model with ZZ interactions
- **LUCJ-Chemistry-Nq**: Local Unitary Cluster Jastrow ansatz for molecular simulation

### Benchmarking Standards
- **Mirror-Nq**: Loschmidt echo circuit (random U followed by U†) testing accumulated errors
- **QVstyle-Nq-dD**: Quantum Volume-inspired random SU(4) layers
- **DeepLinear-Nq-dD**: Deep circuit with repeated linear entanglement

### Utility Circuits
- **ShallowWide-Nq**: Parallel operations testing qubit count limits
- **QAOA-Ring-Nq**: Quantum Approximate Optimization on ring graph

## Recommendations

1. **For >120 qubit circuits**: Use Heron R2 or R3 (Nighthawk excluded)
2. **For 2D grid simulations**: Prefer Nighthawk's square lattice
3. **For deep variational circuits**: Compare R2 vs R3 based on current calibration
4. **For chemistry (LUCJ)**: Heavy-hex topology is designed for this; use largest Heron available
5. **For general benchmarking**: Run the selector to find best current option

## References

- [Qiskit Benchpress](https://github.com/Qiskit/benchpress)
- [qiskit-device-benchmarking](https://github.com/qiskit-community/qiskit-device-benchmarking)
- [LUCJ Ansatz (arXiv:2511.22476)](https://arxiv.org/abs/2511.22476)
- [IBM SQD Tutorial](https://quantum.cloud.ibm.com/docs/en/tutorials/sample-based-quantum-diagonalization)
- [Mirror Circuits / Loschmidt Echo (arXiv:2008.11294)](https://arxiv.org/abs/2008.11294)
