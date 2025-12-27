"""Tests for CircuitScorer functionality."""

import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import CXGate, Measure, XGate
from qiskit.providers import BackendV2
from qiskit.transpiler import InstructionProperties, Target

from enhanced_quantum_backend_selector.backend_analyzer import BackendAnalyzer
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
    analyzer = BackendAnalyzer(mock_backend)
    score_result = analyzer.score_for_circuit(single_xgate_circuit)
    assert score_result.score == 0 - (0.001 + 0.02)
    assert score_result.compatible is True

    assert "Used qubit(s): [0]" in score_result.reasons


def test_score_circuit_single_qubit_gate_same_qubit_three_times(
    single_xgate_circuit_same_qubit_three_times: QuantumCircuit, mock_backend: BackendV2
) -> None:
    """Test scoring with single-qubit gates on the same qubit multiple times."""
    analyzer = BackendAnalyzer(mock_backend)
    score_result = analyzer.score_for_circuit(single_xgate_circuit_same_qubit_three_times)
    expected_error = 3 * 0.001 + 0.02  # Three X gates on qubit 0 plus measurement error
    assert score_result.score == 0 - expected_error
    assert score_result.compatible is True

    assert "Used qubit(s): [0]" in score_result.reasons
