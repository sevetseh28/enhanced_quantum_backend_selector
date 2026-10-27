"""Tests for CircuitScorer functionality."""

import math

import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import CXGate, Measure, XGate
from qiskit.providers import BackendV2
from qiskit.transpiler import InstructionProperties, Target

from enhanced_quantum_backend_selector.circuit_scorer import CircuitScorer


def create_mock_target() -> Target:
    """Create a mock Target for testing purposes.

    Creates a Target with:
    - X gate on qubits 0, 1, 2 with error 0.001 each
    - CX gate on (0,1) and (1,2) with error 0.01 each
    - Measure on qubits 0, 1, 2 with errors 0.02, 0.03, 0.04
    """
    target = Target()

    # Single-qubit X gates with errors
    target.add_instruction(
        XGate(),
        {
            (0,): InstructionProperties(error=0.001),
            (1,): InstructionProperties(error=0.001),
            (2,): InstructionProperties(error=0.001),
        },
    )

    # Two-qubit CX gates with errors
    target.add_instruction(
        CXGate(),
        {
            (0, 1): InstructionProperties(error=0.01),
            (1, 2): InstructionProperties(error=0.01),
        },
    )

    # Measurement with errors
    target.add_instruction(
        Measure(),
        {
            (0,): InstructionProperties(error=0.02),
            (1,): InstructionProperties(error=0.03),
            (2,): InstructionProperties(error=0.04),
        },
    )

    return target


@pytest.fixture
def mock_target() -> Target:
    """Fixture providing a mock Target for testing."""
    return create_mock_target()


@pytest.fixture
def mock_backend(mock_target: Target) -> BackendV2:
    """Fixture providing a mock BackendV2 for testing."""

    class MockBackend(BackendV2):
        def __init__(self, target: Target):
            super().__init__(
                name="mock_backend",
                description="Mock backend for testing",
                backend_version="1.0.0",
            )
            self._target = target
            self._num_qubits = 5
            self._max_circuits = 100

        @property
        def target(self) -> Target:
            return self._target

        @property
        def max_circuits(self) -> int:
            return self._max_circuits

        @property
        def num_qubits(self) -> int:
            return self._num_qubits

        @classmethod
        def _default_options(cls):
            """Return default options for the backend."""
            from qiskit.providers import Options

            return Options(shots=1024)

        def run(self, run_input, **options):
            """Run circuits on the backend (mock implementation)."""
            # Mock implementation - not needed for scoring tests
            raise NotImplementedError("run() not needed for scoring tests")

    return MockBackend(mock_target)


@pytest.fixture
def single_xgate_circuit() -> QuantumCircuit:
    """Fixture providing a simple circuit with one X gate."""
    qc = QuantumCircuit(3)
    qc.x(0)  # Apply X gate on qubit 0
    return qc


@pytest.fixture
def single_xgate_circuit_same_qubit_three_times() -> QuantumCircuit:
    """Fixture providing a circuit with three X gates on the same qubit."""
    qc = QuantumCircuit(3)
    qc.x(0)  # Apply X gate on qubit 0
    qc.x(0)  # Apply X gate again on qubit 0
    qc.x(0)  # Apply X gate again on qubit 0
    return qc


def test_score_circuit_single_qubit_gates(
    single_xgate_circuit: QuantumCircuit, mock_backend: BackendV2
) -> None:
    """Test scoring with single-qubit gates only."""
    scorer = CircuitScorer(mock_backend)
    score_result = scorer.score_circuit(single_xgate_circuit)
    expected_error = 1 - (1 - 0.001) * (1 - 0.02)  # X gate on qubit 0 and its readout
    assert score_result.score == pytest.approx(-expected_error)
    assert score_result.compatible is True

    assert "Used qubit(s): [0]" in score_result.reasons


def test_score_circuit_single_qubit_gate_same_qubit_three_times(
    single_xgate_circuit_same_qubit_three_times: QuantumCircuit, mock_backend: BackendV2
) -> None:
    """Test scoring with single-qubit gates on the same qubit multiple times."""
    scorer = CircuitScorer(mock_backend)
    score_result = scorer.score_circuit(single_xgate_circuit_same_qubit_three_times)
    # Three X gates on qubit 0 plus measurement error
    expected_error = 1 - (1 - 0.001) ** 3 * (1 - 0.02)
    assert score_result.score == pytest.approx(-expected_error)
    assert score_result.compatible is True

    assert "Used qubit(s): [0]" in score_result.reasons


def test_missing_error_uses_device_mean(mock_backend: BackendV2) -> None:
    """A gate with no reported error is charged the mean error of that gate."""
    mock_backend.target.update_instruction_properties("x", (0,), InstructionProperties())
    qc = QuantumCircuit(3)
    qc.x(0)

    score_result = CircuitScorer(mock_backend).score_circuit(qc)

    expected_error = 1 - (1 - 0.001) * (1 - 0.02)  # Mean X error on qubits 1, 2 is 0.001
    assert score_result.score == pytest.approx(-expected_error)


def test_operation_without_any_error_data_is_reported(mock_backend: BackendV2) -> None:
    """Operations with no error data anywhere are listed in the reasons."""
    for qargs in [(0,), (1,), (2,)]:
        mock_backend.target.update_instruction_properties("x", qargs, InstructionProperties())
    qc = QuantumCircuit(3)
    qc.x(0)

    score_result = CircuitScorer(mock_backend).score_circuit(qc)

    assert score_result.score == pytest.approx(-0.02)
    assert "No error data for: ['x']" in score_result.reasons


def test_deep_circuit_score_stays_bounded(mock_backend: BackendV2) -> None:
    """Expected error never exceeds 100%, however deep the circuit."""
    qc = QuantumCircuit(3)
    for _ in range(2000):
        qc.cx(0, 1)

    score_result = CircuitScorer(mock_backend).score_circuit(qc)

    assert -1.0 <= score_result.score < -0.99
    assert not math.isnan(score_result.score)
