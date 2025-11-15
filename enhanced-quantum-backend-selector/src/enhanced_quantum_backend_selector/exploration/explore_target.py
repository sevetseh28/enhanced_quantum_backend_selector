"""
Target Class Exploration Examples (Qiskit 2.2)

This script demonstrates how to inspect and analyze Target objects to understand
backend capabilities. Essential for designing intelligent backend selection logic.

Run this to understand:
1. How Target data is structured
2. What information is available for decision-making
3. How to query specific capabilities
4. How to extract metrics for comparison
"""

import numpy as np
from qiskit.circuit import Instruction, Parameter
from qiskit.circuit.library import ECRGate, Measure, Reset, RZGate, SXGate, XGate
from qiskit.transpiler import InstructionProperties, Target

from enhanced_quantum_backend_selector.models import BackendMetrics


def create_sample_target() -> Target:
    """
    Create a realistic Target representing a small quantum backend.
    This mimics what you'd get from a real IBM backend.

    Returns:
        Target: A sample target with 5 qubits and realistic properties
    """
    target = Target(
        description="Sample 5-qubit backend with heavy-hex-like connectivity",
        num_qubits=5,
        dt=0.222e-9,  # 0.222 nanoseconds
        granularity=16,
        min_length=64,
        pulse_alignment=16,
        acquire_alignment=16,
    )

    # Single qubit gates (available on all qubits)
    single_qubit_gates: list[tuple[str, Instruction]] = [
        ("x", XGate()),
        ("sx", SXGate()),  # sqrt(X) - IBM's native gate
        ("rz", RZGate(Parameter("θ"))),  # Parametrized rotation
        ("reset", Reset()),
    ]

    for gate_name, gate_obj in single_qubit_gates:
        properties: dict[tuple[int, ...], InstructionProperties] = {}
        for qubit in range(5):
            # Vary properties by qubit (realistic variation)
            base_error = 0.0001 + qubit * 0.00002
            base_duration = 35.5e-9 + qubit * 1e-9

            properties[(qubit,)] = InstructionProperties(duration=base_duration, error=base_error)
        target.add_instruction(gate_obj, properties, name=gate_name)

    # Two-qubit gates (connectivity-constrained)
    # Heavy-hex-like connectivity: 0-1-2-3-4 with some cross-connections
    connections: list[tuple[int, int]] = [
        (0, 1),
        (1, 0),  # Bidirectional
        (1, 2),
        (2, 1),
        (2, 3),
        (3, 2),
        (1, 3),
        (3, 1),  # Cross connection
        (3, 4),
        (4, 3),
    ]

    # ECR gate (IBM's native 2-qubit gate)
    ecr_properties: dict[tuple[int, int], InstructionProperties] = {}
    for i, (q0, q1) in enumerate(connections):
        # 2-qubit gates have higher error and longer duration
        ecr_properties[(q0, q1)] = InstructionProperties(
            duration=500e-9 + i * 10e-9, error=0.005 + i * 0.0005
        )
    target.add_instruction(ECRGate(), ecr_properties, name="ecr")

    # Measurement (available on all qubits)
    measure_properties: dict[tuple[int, ...], InstructionProperties] = {}
    for qubit in range(5):
        measure_properties[(qubit,)] = InstructionProperties(
            duration=1000e-9, error=0.01 + qubit * 0.002
        )
    target.add_instruction(Measure(), measure_properties, name="measure")

    # Add qubit properties (T1, T2, frequency)
    from qiskit.providers import QubitProperties

    qubit_props: list[QubitProperties] = []
    for i in range(5):
        qubit_props.append(
            QubitProperties(
                t1=(100 + i * 10) * 1e-6,  # 100-140 microseconds
                t2=(80 + i * 8) * 1e-6,  # 80-112 microseconds
                frequency=(5.0 + i * 0.1) * 1e9,  # 5.0-5.4 GHz
            )
        )
    target.qubit_properties = qubit_props

    return target


def explore_basic_properties(target: Target) -> None:
    """Explore basic Target properties

    Args:
        target: The Target object to explore
    """
    print("=" * 70)
    print("BASIC TARGET PROPERTIES")
    print("=" * 70)

    print(f"\nNumber of qubits: {target.num_qubits}")
    print(f"Description: {target.description}")
    print(f"Timing resolution (dt): {target.dt * 1e9:.3f} ns")
    print(f"Pulse granularity: {target.granularity}")
    print(f"Pulse alignment: {target.pulse_alignment}")

    print(f"\nSupported operations ({len(target.operation_names)} total):")
    for op_name in sorted(target.operation_names):
        print(f"  - {op_name}")


def explore_gate_properties(target: Target) -> None:
    """Explore gate properties and where they're available

    Args:
        target: The Target object to explore
    """
    print("\n" + "=" * 70)
    print("GATE PROPERTIES ANALYSIS")
    print("=" * 70)

    for op_name in sorted(target.operation_names):
        print(f"\n{op_name.upper()}:")

        # Get all qubit configurations for this operation
        qargs_list = target.qargs_for_operation_name(op_name)
        if qargs_list is None or len(qargs_list) == 0:
            print("  Available on all qubits (universal)")
            continue

        qargs_list = list(qargs_list)
        print(f"  Available on {len(qargs_list)} qubit configuration(s)")

        # Categorize by arity (number of qubits)
        if qargs_list and len(qargs_list[0]) == 1:
            print("  Type: Single-qubit gate")
            # Show statistics
            errors: list[float] = [
                target[op_name][qargs].error
                for qargs in qargs_list
                if target[op_name][qargs].error is not None
            ]
            durations: list[float] = [
                target[op_name][qargs].duration
                for qargs in qargs_list
                if target[op_name][qargs].duration is not None
            ]

            if errors:
                print(
                    f"  Error rate: {min(errors):.6f} to {max(errors):.6f} (avg: {np.mean(errors):.6f})"
                )
            if durations:
                print(
                    f"  Duration: {min(durations)*1e9:.2f} to {max(durations)*1e9:.2f} ns (avg: {np.mean(durations)*1e9:.2f} ns)"
                )

        elif qargs_list and len(qargs_list[0]) == 2:
            print("  Type: Two-qubit gate")
            print(f"  Connectivity: {qargs_list}")

            errors = [
                target[op_name][qargs].error
                for qargs in qargs_list
                if target[op_name][qargs].error is not None
            ]
            durations = [
                target[op_name][qargs].duration
                for qargs in qargs_list
                if target[op_name][qargs].duration is not None
            ]

            if errors:
                print(
                    f"  Error rate: {min(errors):.6f} to {max(errors):.6f} (avg: {np.mean(errors):.6f})"
                )
            if durations:
                print(
                    f"  Duration: {min(durations)*1e9:.2f} to {max(durations)*1e9:.2f} ns (avg: {np.mean(durations)*1e9:.2f} ns)"
                )


def explore_connectivity(target: Target) -> None:
    """Analyze qubit connectivity

    Args:
        target: The Target object to explore
    """
    print("\n" + "=" * 70)
    print("CONNECTIVITY ANALYSIS")
    print("=" * 70)

    # Build coupling map from 2-qubit operations
    coupling_map = target.build_coupling_map()

    if coupling_map:
        edges = coupling_map.get_edges()
        print(f"\nCoupling map: {edges}")
        print(f"Number of edges: {len(edges)}")
        print(f"Bidirectional: {coupling_map.is_symmetric}")

        # Analyze connectivity per qubit
        print("\nQubit connectivity (degree):")
        for qubit in range(target.num_qubits):
            neighbors: list[int] = [edge[1] for edge in edges if edge[0] == qubit]
            print(f"  Qubit {qubit}: {len(neighbors)} connections → {neighbors}")
    else:
        print("\nNo connectivity constraints (fully connected or no 2-qubit gates)")


def explore_qubit_properties(target: Target) -> None:
    """Explore per-qubit physical properties

    Args:
        target: The Target object to explore
    """
    print("\n" + "=" * 70)
    print("QUBIT PHYSICAL PROPERTIES")
    print("=" * 70)

    if target.qubit_properties is None:
        print("\nNo qubit properties available")
        return

    print(f"\n{'Qubit':<8} {'T1 (μs)':<12} {'T2 (μs)':<12} {'Frequency (GHz)':<15}")
    print("-" * 50)

    for i, props in enumerate(target.qubit_properties):
        t1: float | None = props.t1 * 1e6 if props.t1 else None
        t2: float | None = props.t2 * 1e6 if props.t2 else None
        freq: float | None = props.frequency * 1e-9 if props.frequency else None

        t1_str = f"{t1:.2f}" if t1 else "N/A"
        t2_str = f"{t2:.2f}" if t2 else "N/A"
        freq_str = f"{freq:.4f}" if freq else "N/A"

        print(f"{i:<8} {t1_str:<12} {t2_str:<12} {freq_str:<15}")

    # Identify best/worst qubits
    if all(p.t1 is not None for p in target.qubit_properties):
        t1_values: list[tuple[int, float]] = [
            (i, p.t1) for i, p in enumerate(target.qubit_properties) if p.t1 is not None
        ]
        best_t1: tuple[int, float] = max(t1_values, key=lambda x: x[1])
        worst_t1: tuple[int, float] = min(t1_values, key=lambda x: x[1])
        print(f"\nBest T1: Qubit {best_t1[0]} ({best_t1[1]*1e6:.2f} μs)")
        print(f"Worst T1: Qubit {worst_t1[0]} ({worst_t1[1]*1e6:.2f} μs)")


def query_specific_operations(target: Target) -> None:
    """Demonstrate querying specific operations

    Args:
        target: The Target object to explore
    """
    print("\n" + "=" * 70)
    print("QUERYING SPECIFIC OPERATIONS")
    print("=" * 70)

    # Check if specific operation is supported
    print("\n1. Checking operation support:")
    for op in ["ecr", "cx", "h", "u3"]:
        supported: bool = op in target.operation_names
        print(f"   {op}: {'✓ Supported' if supported else '✗ Not supported'}")

    # Get properties for specific gate on specific qubits
    print("\n2. Getting properties for ECR gate on qubits (1, 2):")
    if "ecr" in target.operation_names:
        try:
            props: InstructionProperties = target["ecr"][(1, 2)]
            print(f"   Duration: {props.duration * 1e9:.2f} ns")
            print(f"   Error: {props.error * 100:.3f}%")
        except KeyError:
            print("   ECR gate not available on qubits (1, 2)")

    # Find all qubit pairs that support a specific gate
    print("\n3. All qubit pairs supporting ECR gate:")
    if "ecr" in target.operation_names:
        ecr_qargs = target.qargs_for_operation_name("ecr")
        for qargs in sorted(ecr_qargs):
            props = target["ecr"].get(qargs)
            if props:
                print(
                    f"   {qargs}: error={props.error*100:.3f}%, duration={props.duration*1e9:.2f}ns"
                )

    # Find operations available on specific qubits
    print("\n4. Operations available on qubit 2:")
    ops_on_q2: set = target.operation_names_for_qargs((2,))
    print(f"   {sorted(ops_on_q2)}")


def extract_metrics_for_comparison(target: Target) -> BackendMetrics:
    """
    Extract key metrics useful for backend comparison.
    This is what I'd use in my intelligent selector.

    Args:
        target: The Target object to extract metrics from

    Returns:
        BackendMetrics containing extracted metrics for backend comparison
    """
    print("\n" + "=" * 70)
    print("METRICS FOR BACKEND COMPARISON")
    print("=" * 70)

    metrics = BackendMetrics()

    # 1. Average single-qubit gate error
    single_q_errors: list[float] = []
    for op_name in target.operation_names:
        qargs_list = target.qargs_for_operation_name(op_name)
        if qargs_list:
            for qa in qargs_list:
                props = target[op_name].get(qa)
                if props and len(qa) == 1 and props.error is not None:
                    single_q_errors.append(props.error)

    if single_q_errors:
        metrics.avg_1q_error = float(np.mean(single_q_errors))
        metrics.max_1q_error = float(np.max(single_q_errors))
        metrics.min_1q_error = float(np.min(single_q_errors))

    # 2. Average two-qubit gate error
    two_q_errors: list[float] = []
    for op_name in target.operation_names:
        qargs_list = target.qargs_for_operation_name(op_name)
        if qargs_list:
            for qa in qargs_list:
                props = target[op_name].get(qa)
                if props and len(qa) == 2 and props.error is not None:
                    two_q_errors.append(props.error)

    if two_q_errors:
        metrics.avg_2q_error = float(np.mean(two_q_errors))
        metrics.max_2q_error = float(np.max(two_q_errors))
        metrics.min_2q_error = float(np.min(two_q_errors))

    # 3. Measurement errors
    if "measure" in target.operation_names:
        qargs_list = target.qargs_for_operation_name("measure")
        meas_errors: list[float] = [
            target["measure"][qa].error
            for qa in qargs_list
            if target["measure"].get(qa) and target["measure"][qa].error is not None
        ]
        if meas_errors:
            metrics.avg_readout_error = float(np.mean(meas_errors))
            metrics.max_readout_error = float(np.max(meas_errors))

    # 4. Coherence times
    if target.qubit_properties:
        t1_values: list[float] = [p.t1 for p in target.qubit_properties if p.t1 is not None]
        t2_values: list[float] = [p.t2 for p in target.qubit_properties if p.t2 is not None]

        if t1_values:
            metrics.avg_t1 = float(np.mean(t1_values))
            metrics.min_t1 = float(np.min(t1_values))
        if t2_values:
            metrics.avg_t2 = float(np.mean(t2_values))
            metrics.min_t2 = float(np.min(t2_values))

    # 5. Connectivity metrics
    coupling_map = target.build_coupling_map()
    if coupling_map:
        edges = coupling_map.get_edges()
        metrics.num_edges = len(edges)
        metrics.connectivity_ratio = len(edges) / (target.num_qubits * (target.num_qubits - 1))

    # 6. Gate set size
    metrics.num_operations = len(target.operation_names)
    metrics.operations = list(target.operation_names)

    # Print metrics
    print("\nExtracted Metrics:")
    if metrics.avg_1q_error is not None:
        print(f"  avg_1q_error: {metrics.avg_1q_error*100:.4f}%")
        print(f"  max_1q_error: {metrics.max_1q_error*100:.4f}%")
        print(f"  min_1q_error: {metrics.min_1q_error*100:.4f}%")
    if metrics.avg_2q_error is not None:
        print(f"  avg_2q_error: {metrics.avg_2q_error*100:.4f}%")
        print(f"  max_2q_error: {metrics.max_2q_error*100:.4f}%")
        print(f"  min_2q_error: {metrics.min_2q_error*100:.4f}%")
    if metrics.avg_readout_error is not None:
        print(f"  avg_readout_error: {metrics.avg_readout_error*100:.4f}%")
        print(f"  max_readout_error: {metrics.max_readout_error*100:.4f}%")
    if metrics.avg_t1 is not None:
        print(f"  avg_t1: {metrics.avg_t1*1e6:.2f} μs")
        print(f"  min_t1: {metrics.min_t1*1e6:.2f} μs")
    if metrics.avg_t2 is not None:
        print(f"  avg_t2: {metrics.avg_t2*1e6:.2f} μs")
        print(f"  min_t2: {metrics.min_t2*1e6:.2f} μs")
    if metrics.num_edges is not None:
        print(f"  num_edges: {metrics.num_edges}")
        print(f"  connectivity_ratio: {metrics.connectivity_ratio:.6f}")
    print(f"  num_operations: {metrics.num_operations}")
    print(f"  operations: {metrics.operations}")

    return metrics


def main() -> None:
    """Run all exploration examples"""
    print("\n" + "🔬" * 35)
    print("TARGET CLASS EXPLORATION - Qiskit 2.2")
    print("🔬" * 35)

    # Create a sample target
    target = create_sample_target()

    # Run all explorations
    explore_basic_properties(target)
    explore_gate_properties(target)
    explore_connectivity(target)
    explore_qubit_properties(target)
    query_specific_operations(target)
    metrics: BackendMetrics = extract_metrics_for_comparison(target)

    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways for Backend Selection:")
    print("1. Target provides ALL backend capability information")
    print("2. Gate errors vary by qubit and operation")
    print("3. Connectivity constrains 2-qubit gate placement")
    print("4. T1/T2 times indicate decoherence limits")
    print("5. Multiple metrics needed for intelligent comparison")
    print("\nNext: Explore real backend Targets via BackendV2!")


if __name__ == "__main__":
    main()
