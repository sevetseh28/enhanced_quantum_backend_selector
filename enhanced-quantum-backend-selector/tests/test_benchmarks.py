"""Tests for benchmark circuits.

This module tests that all benchmark circuits can be created successfully
and have the expected properties.
"""

import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit_ibm_runtime.fake_provider import FakeTorino

from benchmarks.circuits.benchmark_circuits import (
    create_bernstein_vazirani_circuit,
    create_ghz_circuit,
    create_lucj_ansatz,
    create_mirror_5k_circuit,
    create_qaoa_circuit,
)


class TestBenchmarkCircuits:
    """Tests for benchmark circuit creation."""

    def test_ghz_circuit_creation(self):
        """Test GHZ circuit matches expected reference circuit."""
        qc = create_ghz_circuit(5)

        # Build expected reference circuit for 5-qubit GHZ
        expected = QuantumCircuit(5, name="GHZ-5")
        expected.h(0)
        expected.cx(0, 1)
        expected.cx(1, 2)
        expected.cx(2, 3)
        expected.cx(3, 4)
        expected.measure_all()

        # Check basic properties
        assert isinstance(qc, QuantumCircuit)
        assert qc.num_qubits == expected.num_qubits
        assert qc.num_clbits == expected.num_clbits

        # Check gate counts match exactly
        assert (
            qc.count_ops() == expected.count_ops()
        ), f"Gate counts differ: {qc.count_ops()} vs {expected.count_ops()}"

        # Check circuit depth matches
        assert qc.depth() == expected.depth(), f"Depth differs: {qc.depth()} vs {expected.depth()}"

        # Check circuits are equivalent (ignoring barriers and layout)
        # Remove measurements for operator comparison
        qc_no_meas = qc.remove_final_measurements(inplace=False)
        expected_no_meas = expected.remove_final_measurements(inplace=False)
        assert Operator(qc_no_meas).equiv(
            Operator(expected_no_meas)
        ), "GHZ circuit is not equivalent to expected reference circuit"

    def test_ghz_circuit_invalid_qubits(self):
        """Test GHZ circuit raises error with invalid qubit count."""
        with pytest.raises(ValueError, match="at least 2 qubits"):
            create_ghz_circuit(1)

    def test_bernstein_vazirani_circuit_creation(self):
        """Test Bernstein-Vazirani circuit matches expected reference circuit."""
        qc = create_bernstein_vazirani_circuit(5)  # 5 qubits, hidden string "1111"

        # Build expected reference circuit for 5-qubit BV with all-ones hidden string
        # Circuit: 4 data qubits + 1 ancilla, hidden string = "1111"
        expected = QuantumCircuit(5, name="BV-5")

        # Initialize ancilla qubit in |->
        expected.x(4)
        expected.h(4)

        # Apply Hadamard to all data qubits
        for i in range(4):
            expected.h(i)

        # Apply oracle: CX from each data qubit to ancilla (all bits are 1)
        for i in range(4):
            expected.cx(i, 4)

        # Apply Hadamard to all data qubits
        for i in range(4):
            expected.h(i)

        expected.measure_all()

        # Check basic properties
        assert isinstance(qc, QuantumCircuit)
        assert qc.num_qubits == expected.num_qubits
        assert qc.num_clbits == expected.num_clbits

        # Check gate counts match exactly
        assert (
            qc.count_ops() == expected.count_ops()
        ), f"Gate counts differ: {qc.count_ops()} vs {expected.count_ops()}"

        # Check circuit depth matches
        assert qc.depth() == expected.depth(), f"Depth differs: {qc.depth()} vs {expected.depth()}"

        # Check circuits are equivalent (ignoring barriers and layout)
        qc_no_meas = qc.remove_final_measurements(inplace=False)
        expected_no_meas = expected.remove_final_measurements(inplace=False)
        assert Operator(qc_no_meas).equiv(
            Operator(expected_no_meas)
        ), "BV circuit is not equivalent to expected reference circuit"

    def test_bernstein_vazirani_custom_string(self):
        """Test Bernstein-Vazirani circuit with custom hidden string."""
        qc = create_bernstein_vazirani_circuit(5, hidden_string="1010")
        assert isinstance(qc, QuantumCircuit)
        assert qc.num_qubits == 5

    def test_bernstein_vazirani_invalid_string_length(self):
        """Test Bernstein-Vazirani raises error with wrong string length."""
        with pytest.raises(ValueError, match="length must be"):
            create_bernstein_vazirani_circuit(5, hidden_string="11")

    def test_bernstein_vazirani_invalid_qubits(self):
        """Test Bernstein-Vazirani raises error with insufficient qubits."""
        with pytest.raises(ValueError, match="at least 2 qubits"):
            create_bernstein_vazirani_circuit(1)

    @pytest.mark.slow
    def test_mirror_5k_circuit_creation(self):
        """Test Mirror 5k circuit creation.

        Note: This test is slow due to get_longest_path() computation.
        The mirror circuit uses IBM's qiskit-device-benchmarking implementation.
        """
        backend = FakeTorino()
        num_qubits = 20
        target_num_2q_gates = 100
        qc = create_mirror_5k_circuit(
            backend, num_qubits=num_qubits, target_num_2q_gates=target_num_2q_gates
        )

        assert isinstance(qc, QuantumCircuit)

        # Mirror circuit maps to physical qubits on the longest path
        # The circuit num_qubits equals the backend's total qubits since
        # it uses trivial layout mapping to physical qubit indices
        assert qc.num_qubits > 0

        # Check circuit has expected gate types from 1D Ising Trotter evolution
        ops = qc.count_ops()
        # Mirror circuit should have 2-qubit gates (CZ, ECR, or CX depending on backend)
        assert (
            "cz" in ops or "cx" in ops or "ecr" in ops
        ), f"Mirror circuit should have 2-qubit gates, got: {ops}"

        # Check that parameters are bound (no remaining parameters)
        assert qc.num_parameters == 0, "Mirror circuit parameters should be bound"

        # Check depth is reasonable
        assert qc.depth() > 0

    @pytest.mark.slow
    def test_mirror_circuit_default_parameters(self):
        """Test Mirror circuit with default parameters.

        Note: This test is slow due to get_longest_path() computation.
        """
        backend = FakeTorino()
        qc = create_mirror_5k_circuit(backend)

        assert isinstance(qc, QuantumCircuit)
        # Default uses longest path from backend (up to 100 qubits)
        assert qc.num_qubits > 0

        # Check it has gate operations
        ops = qc.count_ops()
        assert len(ops) > 0, "Mirror circuit should have gates"

    def test_lucj_ansatz_creation(self):
        """Test LUCJ ansatz circuit creation using ffsim."""
        qc = create_lucj_ansatz(4, n_reps=1)
        assert isinstance(qc, QuantumCircuit)
        assert qc.num_qubits == 4
        assert qc.depth() > 0
        # Check for ffsim gates (PrepareHartreeFockJW and UCJOpSpinBalancedJW)
        ops = qc.count_ops()
        assert "hartree_fock_jw" in ops, "LUCJ should have Hartree-Fock reference state"
        assert "ucj_balanced_jw" in ops, "LUCJ should have UCJ operator"

    def test_lucj_ansatz_invalid_odd_qubits(self):
        """Test LUCJ ansatz raises error with odd qubit count."""
        with pytest.raises(ValueError, match="even number of qubits"):
            create_lucj_ansatz(5)  # Odd number, should fail

    def test_lucj_ansatz_invalid_too_few_qubits(self):
        """Test LUCJ ansatz raises error with too few qubits."""
        with pytest.raises(ValueError, match="at least 4 qubits"):
            create_lucj_ansatz(2)  # Less than minimum 4 qubits

    def test_qaoa_circuit_creation(self):
        """Test QAOA circuit matches expected structure for MaxCut on ring graph."""
        qc = create_qaoa_circuit(4, num_layers=1)

        # Check basic properties
        assert isinstance(qc, QuantumCircuit)
        assert qc.num_qubits == 4
        assert qc.num_clbits == 4

        # QAOA circuit structure for 4-qubit ring with 1 layer:
        # - Initial layer: 4 H gates (mixer initialization)
        # - Cost layer: 4 RZZ gates (ZZ interactions: 0-1, 1-2, 2-3, 3-0)
        # - Mixer layer: 4 RX gates (X rotations on each qubit)
        # - Measurements: 4

        # The high-level circuit has QAOA gate, decompose to check structure
        decomposed = qc.decompose().decompose()
        ops = decomposed.count_ops()

        # Check expected gate counts after decomposition
        # Note: H gates may be decomposed to U gates in some versions
        assert (
            ops.get("rzz", 0) == 4
        ), f"Expected 4 RZZ gates for ring connectivity, got {ops.get('rzz', 0)}"
        assert ops.get("rx", 0) == 4, f"Expected 4 RX gates for mixer layer, got {ops.get('rx', 0)}"
        assert ops.get("measure", 0) == 4, f"Expected 4 measurements, got {ops.get('measure', 0)}"

        # Check depth is reasonable (should be around 7 after decomposition)
        assert decomposed.depth() > 0
        assert (
            decomposed.depth() <= 15
        ), f"Depth {decomposed.depth()} seems too high for 1-layer QAOA"

    def test_qaoa_circuit_invalid_qubits(self):
        """Test QAOA raises error with insufficient qubits."""
        with pytest.raises(ValueError, match="at least 2 qubits"):
            create_qaoa_circuit(1)

    def test_qaoa_circuit_invalid_layers(self):
        """Test QAOA raises error with invalid layer count."""
        with pytest.raises(ValueError, match="at least 1 layer"):
            create_qaoa_circuit(4, num_layers=0)

    def test_all_circuits_have_measurements(self):
        """Test that all benchmark circuits include measurements."""
        circuits = [
            create_ghz_circuit(5),
            create_bernstein_vazirani_circuit(5),
            create_lucj_ansatz(4, n_reps=1),
            create_qaoa_circuit(4, num_layers=1),
        ]
        for circuit in circuits:
            assert circuit.num_clbits > 0, f"Circuit {circuit.name} has no classical bits"
            ops = circuit.count_ops()
            assert "measure" in ops, f"Circuit {circuit.name} has no measurements"
