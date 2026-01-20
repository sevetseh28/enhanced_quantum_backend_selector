"""Benchmark circuits implementation for real-world quantum computing tests.

This module implements various real-world quantum circuits used for benchmarking
the Enhanced Quantum Backend Selector. Circuits are based on established quantum
algorithms and benchmarking frameworks from Qiskit Benchpress and qiskit-device-benchmarking.

References:
    - Qiskit Benchpress: https://github.com/Qiskit/benchpress
    - Device Benchmarking: https://github.com/qiskit-community/qiskit-device-benchmarking
    - LUCJ Ansatz: https://arxiv.org/pdf/2511.22476
    - Mirror Circuits: https://github.com/qiskit-community/qiskit-device-benchmarking/blob/main/qiskit_device_benchmarking/mirror_test/mirror_circuits.py

Not published in the registry: https://github.com/qiskit-community/qiskit-device-benchmarking/blob/main/qiskit_device_benchmarking/mirror_test/mirror_circuits.py
Import directly.
"""

from qiskit import QuantumCircuit
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp
from qiskit_device_benchmarking.mirror_test.mirror_pub import MirrorPubOptions


def create_ghz_circuit(num_qubits: int) -> QuantumCircuit:
    """Create a GHZ (Greenberger-Horne-Zeilinger) state circuit.

    GHZ states are maximally entangled states across all qubits, commonly used
    for testing multi-qubit entanglement fidelity and connectivity.

    Args:
        num_qubits: Number of qubits (minimum 2).

    Returns:
        QuantumCircuit implementing GHZ state.

    Raises:
        ValueError: If num_qubits < 2.

    Examples:
        >>> ghz = create_ghz_circuit(5)
        >>> print(f"Depth: {ghz.depth()}, Gates: {ghz.size()}")

    Notes:
        Circuit structure: H(q0), CX(q0,q1), CX(q1,q2), ..., CX(qn-2,qn-1)
        This tests backend suitability for long-range connectivity and CNOT fidelity.
    """
    if num_qubits < 2:
        raise ValueError("GHZ circuit requires at least 2 qubits")

    qc = QuantumCircuit(num_qubits, name=f"GHZ-{num_qubits}")
    qc.h(0)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()

    return qc


def create_bernstein_vazirani_circuit(
    num_qubits: int, hidden_string: str | None = None
) -> QuantumCircuit:
    """Create a Bernstein-Vazirani circuit with all-ones hidden string.

    The Bernstein-Vazirani algorithm finds a hidden binary string in a single query.
    This implementation uses an all-ones string as specified in the benchmarking requirements.

    Args:
        num_qubits: Number of qubits (minimum 2, includes 1 ancilla).
        hidden_string: Hidden binary string. If None, uses all ones (default).

    Returns:
        QuantumCircuit implementing Bernstein-Vazirani algorithm.

    Raises:
        ValueError: If num_qubits < 2 or hidden_string length doesn't match.

    Examples:
        >>> bv = create_bernstein_vazirani_circuit(5)  # All ones string
        >>> bv_custom = create_bernstein_vazirani_circuit(5, "1101")

    Notes:
        Tests parallel operations, phase kickback, and Hadamard transform efficiency.
        Reference: https://github.com/Qiskit/benchpress
    """
    if num_qubits < 2:
        raise ValueError("Bernstein-Vazirani requires at least 2 qubits (including ancilla)")

    n = num_qubits - 1  # Number of qubits for the hidden string
    if hidden_string is None:
        hidden_string = "1" * n
    elif len(hidden_string) != n:
        raise ValueError(f"Hidden string length must be {n}, got {len(hidden_string)}")

    qc = QuantumCircuit(num_qubits, name=f"BV-{num_qubits}")

    # Initialize ancilla qubit in |->
    qc.x(num_qubits - 1)
    qc.h(num_qubits - 1)

    # Apply Hadamard to all data qubits
    for i in range(n):
        qc.h(i)

    # Apply oracle (controlled-X based on hidden string)
    for i, bit in enumerate(hidden_string):
        if bit == "1":
            qc.cx(i, num_qubits - 1)

    # Apply Hadamard to all data qubits
    for i in range(n):
        qc.h(i)

    qc.measure_all()

    return qc


def create_mirror_circuit(
    backend,
    num_qubits: int = 100,
    target_num_2q_gates: int = 4986,
    theta: float = 0.0,
    path: tuple[int, ...] | None = None,
) -> QuantumCircuit:
    """Create a 1D Ising mirror circuit using IBM's qiskit-device-benchmarking.

    Uses the official IBM mirror circuit implementation: Trotterized 1D Ising model
    evolution followed by its inverse (U†U = I). In a perfect quantum computer,
    this returns all expectation values = 1.

    This function follows the qiskit-device-benchmarking repo exactly by:
    1. Using MirrorPubOptions to configure the circuit parameters
    2. Generating the EstimatorPub via get_pubs()
    3. Extracting the parameterized circuit from the pub
    4. Binding parameters to fixed values for benchmarking

    The circuit structure is:
    - Forward: Trotter steps of H = Σ X_i + Σ ZZ_{ij}
    - Mirror: Inverse of forward circuit
    - Contrast rotation Rx(delta) for magnetization measurement

    Args:
        backend: IBM backend (real or fake) to get basis gates and coupling map.
        num_qubits: Number of qubits for the 1D chain path (default 100).
        target_num_2q_gates: Target number of 2-qubit gates (default 4986, matching
            IBM's standard benchmark). This determines the number of Trotter steps.
        theta: Rotation angle for 1Q gates in Trotter step (default 0.0). Non-zero
            values spread entanglement across time steps.
        path: Optional tuple of physical qubit indices defining the 1D chain path.
            If None, the longest path from the backend's coupling map is used.

    Returns:
        QuantumCircuit implementing IBM's mirrored Trotter benchmark with bound parameters.

    Examples:
        >>> from qiskit_ibm_runtime.fake_provider import FakeTorino
        >>> mirror = create_mirror_circuit(FakeTorino(), num_qubits=50, target_num_2q_gates=1000)
        >>> print(f"Qubits: {mirror.num_qubits}, Depth: {mirror.depth()}")

    Notes:
        Reference: qiskit-community/qiskit-device-benchmarking/mirror_test
        Tests: Accumulated gate errors over utility-scale Trotter evolution.
    """
    # Configure pub options following the device benchmarking repo exactly
    pub_options = MirrorPubOptions()
    pub_options.num_qubits = num_qubits
    pub_options.target_num_2q_gates = target_num_2q_gates
    pub_options.theta = theta
    pub_options.path = path
    # Use None for path_strategy to use the longest path from coupling map
    pub_options.path_strategy = None

    # Generate the pub using the repo's method
    pubs = pub_options.get_pubs(backend)

    # Extract the parameterized circuit from the first pub element
    parameterized_circuit = pubs[0].circuit

    # Bind parameters to fixed values for benchmarking
    bound_circuit = parameterized_circuit.assign_parameters([0, 0], inplace=False)

    return bound_circuit


# Keep alias for backward compatibility
def create_mirror_5k_circuit(
    backend, num_qubits: int = 100, target_num_2q_gates: int = 4986
) -> QuantumCircuit:
    """Alias for create_mirror_circuit (backward compatibility).

    The '5k' refers to ~5000 2-qubit gates (default 4986 matches IBM's benchmark).
    """
    return create_mirror_circuit(backend, num_qubits, target_num_2q_gates)


def create_lucj_ansatz(
    num_qubits: int = 52, n_reps: int = 1, topology: str = "heavy_hex"
) -> QuantumCircuit:
    """Create a LUCJ (Local Unitary Cluster Jastrow) ansatz for chemistry applications.

    LUCJ is a hardware-efficient chemistry ansatz combining orbital rotations (e^K)
    with Jastrow correlations (e^iJ). The "local" variant restricts interactions
    to match hardware connectivity, enabling constant-depth implementation.

    This implementation uses the ffsim package's UCJOpSpinBalanced to create an
    authentic LUCJ ansatz following the IBM SQD tutorial:
    https://quantum.cloud.ibm.com/docs/en/tutorials/sample-based-quantum-diagonalization

    The ansatz structure per layer is: e^K * e^iJ * e^-K where:
    - K: orbital rotation (Givens rotations in linear depth)
    - J: diagonal correlations with connectivity-aware sparsity

    Args:
        num_qubits: Number of qubits (must be even for spin orbitals, minimum 4).
        n_reps: Number of UCJ repetitions (default 1).
        topology: Target topology - "heavy_hex" (Heron) or "square" (Nighthawk).

    Returns:
        QuantumCircuit implementing LUCJ ansatz with Hartree-Fock reference state.

    Raises:
        ValueError: If num_qubits < 4 or is odd.

    Examples:
        >>> lucj = create_lucj_ansatz(52, n_reps=1, topology="heavy_hex")
        >>> print(f"Depth: {lucj.depth()}, 2Q gates: {lucj.num_nonlocal_gates()}")

    Notes:
        Reference: https://quantum.cloud.ibm.com/docs/en/tutorials/sample-based-quantum-diagonalization
        Paper: arXiv:2511.22476 (Improved parameter initialization for LUCJ)
        Uses ffsim UCJOpSpinBalanced implementation with PrepareHartreeFockJW.

        Heavy-hex topology (Heron R1/R2/R3): zig-zag qubit layout
        - J_αα: (p, p+1) for p = 0..N-2 (same-spin neighbors)
        - J_αβ: (p, p) for p = 0, 4, 8... (cross-spin every 4th orbital)

        Square topology (Nighthawk): ladder qubit layout
        - J_αα: (p, p+1) for p = 0..N-2 (same-spin neighbors)
        - J_αβ: (p, p) for all p (cross-spin at same spatial orbital)
    """
    import ffsim
    import numpy as np
    from qiskit.circuit import QuantumRegister

    if num_qubits < 4:
        raise ValueError("LUCJ ansatz requires at least 4 qubits")
    if num_qubits % 2 != 0:
        raise ValueError("LUCJ ansatz requires even number of qubits (spin orbitals)")

    num_orbitals = num_qubits // 2  # spatial orbitals (α and β spins)

    # Define electron configuration (half-filling for benchmark)
    # For a realistic chemistry circuit, we occupy half of the orbitals
    num_elec_a = num_orbitals // 2  # α electrons
    num_elec_b = num_orbitals // 2  # β electrons
    nelec = (num_elec_a, num_elec_b)

    # Define interaction pairs based on topology (following SQD tutorial)
    # J_αα: same-spin interactions (p, p+1) for all topologies
    alpha_alpha_indices = [(p, p + 1) for p in range(num_orbitals - 1)]

    # J_αβ: cross-spin interactions depend on topology
    if topology == "heavy_hex":
        # Heavy-hex (Heron): zig-zag pattern, cross-spin every 4th orbital
        alpha_beta_indices = [(p, p) for p in range(0, num_orbitals, 4)]
    else:  # square lattice (Nighthawk)
        # Square lattice: ladder pattern, cross-spin at all spatial orbitals
        alpha_beta_indices = [(p, p) for p in range(num_orbitals)]

    # Generate random t1 and t2 amplitudes for benchmark purposes
    # In real applications, these come from CCSD calculations
    rng = np.random.default_rng(seed=42)  # Fixed seed for reproducibility

    # t1 amplitudes: shape (num_elec_a, num_orbitals - num_elec_a)
    # Represents single excitations from occupied to virtual orbitals
    n_occ = num_elec_a
    n_virt = num_orbitals - num_elec_a
    t1 = rng.standard_normal((n_occ, n_virt)) * 0.1

    # t2 amplitudes: shape (num_elec_a, num_elec_a, n_virt, n_virt)
    # Represents double excitations
    t2 = rng.standard_normal((n_occ, n_occ, n_virt, n_virt)) * 0.05
    # Make t2 antisymmetric as required for fermionic amplitudes
    t2 = t2 - t2.transpose(1, 0, 2, 3)
    t2 = t2 - t2.transpose(0, 1, 3, 2)

    # Create UCJ operator from t-amplitudes using ffsim (following SQD tutorial)
    ucj_op = ffsim.UCJOpSpinBalanced.from_t_amplitudes(
        t2=t2,
        t1=t1,
        n_reps=n_reps,
        interaction_pairs=(alpha_alpha_indices, alpha_beta_indices),
        # Setting optimize=True enables the "compressed" factorization
        optimize=True,
        # Limit optimization iterations for benchmarking
        options={"maxiter": 1000},
    )

    # Create the quantum circuit
    qubits = QuantumRegister(2 * num_orbitals, name="q")
    circuit = QuantumCircuit(qubits, name=f"LUCJ-{num_qubits}q-{n_reps}rep-{topology}")

    # Prepare Hartree-Fock state as the reference state (following SQD tutorial)
    circuit.append(ffsim.qiskit.PrepareHartreeFockJW(num_orbitals, nelec), qubits)

    # Apply the UCJ operator to the reference state (following SQD tutorial)
    circuit.append(ffsim.qiskit.UCJOpSpinBalancedJW(ucj_op), qubits)

    # Add measurements
    circuit.measure_all()

    return circuit


def create_qaoa_circuit(num_qubits: int = 4, num_layers: int = 1) -> QuantumCircuit:
    """Create a QAOA (Quantum Approximate Optimization Algorithm) circuit.

    QAOA is used for solving combinatorial optimization problems. This implementation
    creates a QAOA circuit for the MaxCut problem on a ring graph.

    Args:
        num_qubits: Number of qubits (minimum 2).
        num_layers: Number of QAOA layers (p parameter, default 1).

    Returns:
        QuantumCircuit implementing QAOA for MaxCut.

    Raises:
        ValueError: If num_qubits < 2 or num_layers < 1.

    Examples:
        >>> qaoa = create_qaoa_circuit(4, num_layers=2)
        >>> print(f"Depth: {qaoa.depth()}")

    Notes:
        Tests backend suitability for:
        - Optimization algorithms
        - Variational circuits
        - Alternating unitaries
        Reference: Qiskit Benchpress
    """
    if num_qubits < 2:
        raise ValueError("QAOA requires at least 2 qubits")
    if num_layers < 1:
        raise ValueError("QAOA requires at least 1 layer")

    # Define MaxCut problem on a ring graph
    # Cost Hamiltonian: sum of Z_i Z_{i+1} for ring connectivity
    pauli_list = []
    for i in range(num_qubits):
        # Ring connectivity: connect each qubit to next (with wraparound)
        j = (i + 1) % num_qubits
        pauli_str = ["I"] * num_qubits
        pauli_str[i] = "Z"
        pauli_str[j] = "Z"
        pauli_list.append(("".join(pauli_str), 1.0))

    cost_operator = SparsePauliOp.from_list(pauli_list)

    # Create QAOA ansatz
    qaoa_ansatz = QAOAAnsatz(cost_operator, reps=num_layers)

    # Convert to circuit with specific parameter values
    qc = QuantumCircuit(num_qubits, name=f"QAOA-{num_qubits}q-{num_layers}L")

    # Bind parameters to specific values for benchmarking
    params = [0.1 * (i + 1) for i in range(qaoa_ansatz.num_parameters)]
    bound_ansatz = qaoa_ansatz.assign_parameters(params)

    qc.compose(bound_ansatz, inplace=True)
    qc.measure_all()

    return qc


def create_2d_grid_ising(rows: int = 4, cols: int = 4, num_layers: int = 2) -> QuantumCircuit:
    """Create a 2D transverse-field Ising model circuit.

    Simulates a 2D grid of spins with nearest-neighbor ZZ interactions and
    transverse X field. This circuit naturally favors square/grid topologies.

    Args:
        rows: Number of rows in the grid (default 4).
        cols: Number of columns in the grid (default 4).
        num_layers: Number of Trotter steps (default 2).

    Returns:
        QuantumCircuit implementing 2D Ising evolution.

    Notes:
        Favors: Nighthawk (square lattice) due to native 2D grid connectivity.
        Tests: Grid connectivity, 2D nearest-neighbor interactions.
    """
    num_qubits = rows * cols
    qc = QuantumCircuit(num_qubits, name=f"Ising2D-{rows}x{cols}-{num_layers}L")

    # Initialize in |+⟩ state
    for i in range(num_qubits):
        qc.h(i)

    def qubit_index(r: int, c: int) -> int:
        return r * cols + c

    for layer in range(num_layers):
        dt = 0.1 * (layer + 1)

        # ZZ interactions along rows
        for r in range(rows):
            for c in range(cols - 1):
                q0, q1 = qubit_index(r, c), qubit_index(r, c + 1)
                qc.cx(q0, q1)
                qc.rz(dt, q1)
                qc.cx(q0, q1)

        # ZZ interactions along columns
        for r in range(rows - 1):
            for c in range(cols):
                q0, q1 = qubit_index(r, c), qubit_index(r + 1, c)
                qc.cx(q0, q1)
                qc.rz(dt, q1)
                qc.cx(q0, q1)

        # Transverse field (X rotations)
        for i in range(num_qubits):
            qc.rx(dt * 0.5, i)

    qc.measure_all()
    return qc


def create_shallow_wide_circuit(num_qubits: int = 100) -> QuantumCircuit:
    """Create a shallow circuit using many qubits in parallel.

    Tests ability to execute many parallel operations with minimal depth.
    Favors backends with high qubit count and good parallel gate fidelity.

    Args:
        num_qubits: Number of qubits (default 100).

    Returns:
        QuantumCircuit with parallel operations.

    Notes:
        Favors: High qubit count backends (Heron R2/R3 at 156q).
        Excludes: Nighthawk (120q) for circuits > 120 qubits.
        Tests: Parallel execution, readout fidelity.
    """
    qc = QuantumCircuit(num_qubits, name=f"ShallowWide-{num_qubits}q")

    # Layer 1: All H gates (parallel)
    for i in range(num_qubits):
        qc.h(i)

    # Layer 2: Parallel CX on even-odd pairs
    for i in range(0, num_qubits - 1, 2):
        qc.cx(i, i + 1)

    # Layer 3: Parallel CX on odd-even pairs
    for i in range(1, num_qubits - 1, 2):
        qc.cx(i, i + 1)

    # Layer 4: Single qubit rotations
    for i in range(num_qubits):
        qc.rz(0.1, i)

    qc.measure_all()
    return qc


def create_deep_linear_circuit(num_qubits: int = 20, depth: int = 50) -> QuantumCircuit:
    """Create a deep circuit with linear (chain) connectivity.

    Tests sustained operation fidelity over many layers with simple connectivity.
    Favors backends with best coherence times and gate fidelity.

    Args:
        num_qubits: Number of qubits (default 20).
        depth: Number of entangling layers (default 50).

    Returns:
        QuantumCircuit with repeated linear entanglement.

    Notes:
        Favors: Lowest error rate backends (Heron R3 expected).
        Tests: Coherence, accumulated gate errors, linear connectivity.
    """
    qc = QuantumCircuit(num_qubits, name=f"DeepLinear-{num_qubits}q-d{depth}")

    # Initialize
    for i in range(num_qubits):
        qc.h(i)

    # Repeated linear entanglement layers
    for d in range(depth):
        theta = 0.05 * ((d % 10) + 1)
        # Forward pass
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
            qc.rz(theta, i + 1)
        # Single qubit layer
        for i in range(num_qubits):
            qc.ry(theta, i)

    qc.measure_all()
    return qc
