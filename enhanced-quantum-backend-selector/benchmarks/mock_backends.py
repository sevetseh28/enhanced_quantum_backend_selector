"""Fake backends from qiskit-ibm-runtime for benchmarking.

Provides FakeTorino (Heron R1), FakeMarrakesh (Heron R2), FakeBoston (Heron R3),
and FakeMiami (Nighthawk R1).
"""

import os

from qiskit.providers import BackendV2
from qiskit_ibm_runtime.fake_provider import (
    FakeMarrakesh,
    FakeTorino,
)
from qiskit_ibm_runtime.fake_provider.fake_backend import FakeBackendV2


class FakeBoston(FakeBackendV2):
    """A fake 156 qubit IBM Quantum Boston backend (Heron R3).

    This backend is based on real calibration data from ibm_boston with:
    - 156 qubits arranged in heavy-hex topology
    - CZ as the native two-qubit gate
    - Latest Heron generation with best error rates
    """

    dirname = os.path.join(os.path.dirname(__file__), "backend_props")
    conf_filename = "conf_boston.json"
    props_filename = "props_boston.json"
    backend_name = "fake_boston"


class FakeMiami(FakeBackendV2):
    """A fake 120 qubit IBM Quantum Miami backend with square lattice topology.
    Nighthawk r1 processor family.
    """

    dirname = os.path.join(os.path.dirname(__file__), "backend_props")
    conf_filename = "conf_miami.json"
    props_filename = "props_miami.json"
    backend_name = "fake_miami"


def create_mock_heron_r1() -> FakeTorino:
    """Create FakeTorino backend (IBM Heron R1, 133 qubits)."""
    return FakeTorino()


def create_mock_heron_r2() -> FakeMarrakesh:
    """Create FakeMarrakesh backend (IBM Heron R2, 156 qubits)."""
    return FakeMarrakesh()


def create_mock_heron_r3() -> FakeBoston:
    """Create FakeBoston backend (IBM Heron R3, 156 qubits)."""
    return FakeBoston()


def create_mock_miami() -> FakeMiami:
    """Create FakeMiami backend (IBM Miami, 120 qubits, square lattice)."""
    return FakeMiami()


def get_all_mock_backends() -> list[BackendV2]:
    """Return list of all mock backends."""
    return [
        create_mock_heron_r1(),
        create_mock_heron_r2(),
        create_mock_heron_r3(),
        create_mock_miami(),
    ]


def get_backend_info(backend: BackendV2) -> dict[str, str]:
    """Get metadata dict (name, description, strengths, processor_type, generation)."""
    info_map = {
        "fake_torino": {
            "name": "IBM Quantum Heron R1 (FakeTorino)",
            "description": "IBM Quantum Heron R1 - 133 qubit processor with heavy-hex topology",
            "strengths": "Real device calibration data, up to 1,800 two-qubit gates",
            "processor_type": "Heron R1",
            "generation": "2023",
        },
        "fake_marrakesh": {
            "name": "IBM Quantum Heron R2 (FakeMarrakesh)",
            "description": "IBM Quantum Heron R2 - 156 qubit processor with heavy-hex topology",
            "strengths": "Deep circuits (5,000 gates), improved TLS mitigation, high fidelity",
            "processor_type": "Heron R2",
            "generation": "2024",
        },
        "fake_boston": {
            "name": "IBM Quantum Heron R3 (FakeBoston)",
            "description": "IBM Quantum Heron R3 - 156 qubit processor with heavy-hex topology",
            "strengths": "Latest Heron generation, best error rates, highest fidelity, CZ gate",
            "processor_type": "Heron R3",
            "generation": "2025",
        },
        "fake_miami": {
            "name": "IBM Quantum Nighthawk (FakeMiami)",
            "description": "IBM Quantum Nighthawk - 120 qubit processor with square lattice",
            "strengths": "Superior connectivity (4 neighbors/qubit), square lattice, CZ gate",
            "processor_type": "Nighthawk",
            "generation": "2025",
        },
    }

    return info_map.get(
        backend.name,
        {
            "name": backend.name,
            "description": f"Generic backend with {backend.num_qubits} qubits",
            "strengths": "General purpose",
            "processor_type": "Unknown",
            "generation": "Unknown",
        },
    )
