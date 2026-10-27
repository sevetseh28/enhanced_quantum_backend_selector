"""Tests for CircuitScorer functionality."""

import math

import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import CXGate, Measure, XGate
from qiskit.providers import BackendV2, QubitProperties
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


def test_log_success_probability_separates_saturated_scores(mock_backend: BackendV2) -> None:
    """When score rounds to -1.0, the log success probability still orders circuits."""
    scorer = CircuitScorer(mock_backend)
    results = []
    for depth in (5000, 6000):
        qc = QuantumCircuit(3)
        for _ in range(depth):
            qc.cx(0, 1)
        results.append(scorer.score_circuit(qc))

    assert results[0].score == results[1].score == -1.0
    assert results[0].log_success_probability > results[1].log_success_probability
    assert results[0].log_success_probability == pytest.approx(
        5000 * math.log(1 - 0.01) + math.log(1 - 0.02) + math.log(1 - 0.03)
    )


T1, T2 = 100e-6, 80e-6
X_TIME, CX_TIME, MEASURE_TIME = 50e-9, 300e-9, 1e-6


def idle_fidelity(idle: float, t1: float = T1, t2: float = T2) -> float:
    """Average fidelity of a qubit idle for ``idle`` seconds under T1/T2 decay."""
    return 0.5 + math.exp(-idle / t1) / 6 + math.exp(-idle / t2) / 3


def create_timed_target(qubit_properties: list[QubitProperties] | None = None) -> Target:
    """The mock target with gate durations and T1/T2 added, and the same error rates."""
    if qubit_properties is None:
        qubit_properties = [QubitProperties(t1=T1, t2=T2) for _ in range(3)]
    target = Target(qubit_properties=qubit_properties, dt=1e-9)
    target.add_instruction(
        XGate(), {(q,): InstructionProperties(error=0.001, duration=X_TIME) for q in range(3)}
    )
    target.add_instruction(
        CXGate(),
        {qargs: InstructionProperties(error=0.01, duration=CX_TIME) for qargs in [(0, 1), (1, 2)]},
    )
    target.add_instruction(
        Measure(),
        {
            (q,): InstructionProperties(error=error, duration=MEASURE_TIME)
            for q, error in enumerate([0.02, 0.03, 0.04])
        },
    )
    return target


@pytest.fixture
def timed_backend(mock_backend: BackendV2) -> BackendV2:
    """The mock backend with gate durations and T1/T2."""
    mock_backend._target = create_timed_target()
    return mock_backend


def test_idle_error_counts_wait_after_entangling(timed_backend: BackendV2) -> None:
    """A qubit waiting for others after its last gate pays idle error for the wait."""
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.x(1)
    qc.x(1)
    qc.x(1)
    qc.measure_all()

    score_result = CircuitScorer(timed_backend).score_circuit(qc)

    # Qubit 0 waits while qubit 1 runs three X gates; qubit 1 is never idle
    gates_and_readout = (1 - 0.01) * (1 - 0.001) ** 3 * (1 - 0.02) * (1 - 0.03)
    expected = gates_and_readout * idle_fidelity(3 * X_TIME)
    assert score_result.log_success_probability == pytest.approx(math.log(expected))
    assert "Idle time: 0.1 us in total, idle success probability 0.999" in score_result.reasons


def test_idle_error_ignores_wait_before_first_gate(timed_backend: BackendV2) -> None:
    """Qubits are scheduled as late as possible, so waiting in the ground state is free."""
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.x(1)
    qc.x(1)
    qc.x(1)
    qc.measure_all()

    score_result = CircuitScorer(timed_backend).score_circuit(qc)

    expected = (1 - 0.001) ** 4 * (1 - 0.02) * (1 - 0.03)
    assert score_result.log_success_probability == pytest.approx(math.log(expected))
    assert not any(reason.startswith("Idle time") for reason in score_result.reasons)


@pytest.mark.parametrize(("duration", "unit"), [(2, "us"), (2000, "dt")])
def test_delay_counts_as_idle_time(timed_backend: BackendV2, duration: int, unit: str) -> None:
    """Explicit delays between operations are idle time, in seconds or in dt."""
    qc = QuantumCircuit(1)
    qc.x(0)
    qc.delay(duration, 0, unit=unit)
    qc.measure_all()

    score_result = CircuitScorer(timed_backend).score_circuit(qc)

    expected = (1 - 0.001) * (1 - 0.02) * idle_fidelity(2e-6)
    assert score_result.log_success_probability == pytest.approx(math.log(expected))


def test_missing_duration_and_coherence_use_device_mean(mock_backend: BackendV2) -> None:
    """Missing durations and T1/T2 fall back to the device means instead of zero."""
    # Qubit 0 has no T1/T2; the mean of qubits 1 and 2 is (2 * T1, 2 * T2)
    target = create_timed_target(
        [QubitProperties(), QubitProperties(t1=T1, t2=T2), QubitProperties(t1=3 * T1, t2=3 * T2)]
    )
    target.update_instruction_properties("x", (1,), InstructionProperties(error=0.001))
    mock_backend._target = target
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.x(1)
    qc.measure_all()

    score_result = CircuitScorer(mock_backend).score_circuit(qc)

    # Qubit 0 waits for one X gate of the mean X duration, with the mean T1/T2
    gates_and_readout = (1 - 0.01) * (1 - 0.001) * (1 - 0.02) * (1 - 0.03)
    expected = gates_and_readout * idle_fidelity(X_TIME, 2 * T1, 2 * T2)
    assert score_result.log_success_probability == pytest.approx(math.log(expected))


def test_no_idle_error_without_coherence_data(mock_backend: BackendV2) -> None:
    """Backends that report durations but no T1/T2 get no idle error."""
    mock_backend._target = create_timed_target([QubitProperties() for _ in range(3)])
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.x(1)
    qc.measure_all()

    score_result = CircuitScorer(mock_backend).score_circuit(qc)

    expected = (1 - 0.01) * (1 - 0.001) * (1 - 0.02) * (1 - 0.03)
    assert score_result.log_success_probability == pytest.approx(math.log(expected))
