"""
Canonical quantum circuits for testing and validation.

This module provides standard quantum circuits used to validate backend
selection quality and ensure recommendations outperform simple heuristics.
"""

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT


def create_ghz_circuit(num_qubits: int) -> QuantumCircuit:
    """
    Create a Greenberger-Horne-Zeilinger (GHZ) state circuit.

    GHZ states test multi-qubit entanglement and long-range connectivity.
    The circuit creates maximal entanglement across all qubits.

    Circuit structure:
    - Hadamard on first qubit
    - Chain of CNOT gates connecting all qubits

    Args:
        num_qubits: Number of qubits in the GHZ state (minimum 2).

    Returns:
        QuantumCircuit creating a GHZ state.

    Raises:
        ValueError: If num_qubits < 2.

    Examples:
        >>> ghz3 = create_ghz_circuit(3)
        >>> print(ghz3.depth())  # Circuit depth
        >>> ghz5 = create_ghz_circuit(5)
        >>> print(f"Gates: {ghz5.size()}")

    Notes:
        Tests backend suitability for:
        - Multi-qubit entanglement fidelity
        - Long-range qubit connectivity
        - CNOT gate error rates
    """
    if num_qubits < 2:
        raise ValueError("GHZ circuit requires at least 2 qubits")

    qc = QuantumCircuit(num_qubits, name=f"GHZ-{num_qubits}")

    # Create GHZ state: |0...0⟩ + |1...1⟩
    qc.h(0)  # Hadamard on first qubit
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)  # Chain of CNOTs

    qc.measure_all()

    return qc


def create_qft_circuit(num_qubits: int) -> QuantumCircuit:
    """
    Create a Quantum Fourier Transform (QFT) circuit.

    QFT circuits test circuit depth handling and coherence time requirements
    due to their sequential structure and increasing number of controlled
    rotations.

    Args:
        num_qubits: Number of qubits for the QFT (minimum 2).

    Returns:
        QuantumCircuit implementing QFT.

    Raises:
        ValueError: If num_qubits < 2.

    Examples:
        >>> qft4 = create_qft_circuit(4)
        >>> print(f"Depth: {qft4.depth()}")
        >>> qft8 = create_qft_circuit(8)
        >>> print(f"Two-qubit gates: {qft8.num_nonlocal_gates()}")

    Notes:
        Tests backend suitability for:
        - Deep circuit execution
        - Coherence time (T1, T2) requirements
        - Single and two-qubit gate fidelity
        - Sequential operation execution
    """
    if num_qubits < 2:
        raise ValueError("QFT circuit requires at least 2 qubits")

    qc = QuantumCircuit(num_qubits, name=f"QFT-{num_qubits}")

    # Use Qiskit's built-in QFT
    qft = QFT(num_qubits)
    qc.compose(qft, inplace=True)

    qc.measure_all()

    return qc


def create_vqe_ansatz(num_qubits: int, ansatz_type: str = "hardware_efficient") -> QuantumCircuit:
    """
    Create a Variational Quantum Eigensolver (VQE) ansatz circuit.

    VQE ansätze test gate set compatibility and connectivity patterns with
    parameterized circuits typical of variational algorithms.

    Args:
        num_qubits: Number of qubits for the ansatz (minimum 2).
        ansatz_type: Type of ansatz to create.
            - "hardware_efficient": RY + CNOT layers (default)
            - "linear": Linear entanglement pattern
            - "circular": Circular entanglement pattern

    Returns:
        QuantumCircuit implementing the VQE ansatz.

    Raises:
        ValueError: If num_qubits < 2 or ansatz_type is invalid.

    Examples:
        >>> # Hardware-efficient ansatz (default)
        >>> vqe = create_vqe_ansatz(4)
        >>>
        >>> # Linear entanglement pattern
        >>> vqe_linear = create_vqe_ansatz(4, "linear")
        >>>
        >>> # Circular entanglement
        >>> vqe_circular = create_vqe_ansatz(4, "circular")

    Notes:
        Tests backend suitability for:
        - Native gate set compatibility (RY, CNOT)
        - Connectivity patterns matching circuit structure
        - Two-qubit gate error rates
        - Parameter optimization overhead
    """
    if num_qubits < 2:
        raise ValueError("VQE ansatz requires at least 2 qubits")

    if ansatz_type not in ["hardware_efficient", "linear", "circular"]:
        raise ValueError(
            f"Invalid ansatz_type: {ansatz_type}. "
            "Must be 'hardware_efficient', 'linear', or 'circular'"
        )

    qc = QuantumCircuit(num_qubits, name=f"VQE-{ansatz_type}-{num_qubits}")

    # Create hardware-efficient ansatz with 2 layers
    num_layers = 2

    for layer in range(num_layers):
        # Rotation layer (single-qubit gates)
        for qubit in range(num_qubits):
            qc.ry(0.1 * (layer + 1), qubit)  # Parameterized RY gates

        # Entanglement layer (two-qubit gates)
        if ansatz_type == "hardware_efficient" or ansatz_type == "linear":
            # Linear entanglement: 0-1, 1-2, 2-3, ...
            for qubit in range(num_qubits - 1):
                qc.cx(qubit, qubit + 1)

        elif ansatz_type == "circular":
            # Circular entanglement: 0-1, 1-2, ..., (n-1)-0
            for qubit in range(num_qubits - 1):
                qc.cx(qubit, qubit + 1)
            qc.cx(num_qubits - 1, 0)  # Close the circle

    qc.measure_all()

    return qc


def create_random_circuit(num_qubits: int, depth: int, seed: int = 42) -> QuantumCircuit:
    """
    Create a random quantum circuit for general-purpose testing.

    Random circuits test general backend capabilities without specific
    structure assumptions. Useful for benchmarking overall performance.

    Args:
        num_qubits: Number of qubits in the circuit (minimum 1).
        depth: Circuit depth (number of gate layers, minimum 1).
        seed: Random seed for reproducibility.

    Returns:
        QuantumCircuit with random gates.

    Raises:
        ValueError: If num_qubits < 1 or depth < 1.

    Examples:
        >>> # Small random circuit
        >>> random = create_random_circuit(3, depth=5)
        >>>
        >>> # Larger circuit for stress testing
        >>> random_large = create_random_circuit(10, depth=20)
        >>>
        >>> # Reproducible random circuit
        >>> random1 = create_random_circuit(4, 10, seed=123)
        >>> random2 = create_random_circuit(4, 10, seed=123)
        >>> assert random1 == random2  # Same circuit

    Notes:
        Tests backend suitability for:
        - General-purpose quantum computation
        - Mix of single and two-qubit gates
        - Varied connectivity requirements
        - No specific structure assumptions
    """
    if num_qubits < 1:
        raise ValueError("Random circuit requires at least 1 qubit")

    if depth < 1:
        raise ValueError("Circuit depth must be at least 1")

    from qiskit.circuit.random import random_circuit

    qc = random_circuit(
        num_qubits=num_qubits,
        depth=depth,
        seed=seed,
        measure=True,
    )

    qc.name = f"Random-{num_qubits}q-{depth}d"

    return qc
