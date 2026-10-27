"""
Enhanced Quantum Backend Selector

A library for intelligent quantum backend selection using transpilation-based error analysis.
"""

from importlib.metadata import PackageNotFoundError, version

from enhanced_quantum_backend_selector.backend_selector import BackendSelector
from enhanced_quantum_backend_selector.circuit_scorer import CircuitScorer
from enhanced_quantum_backend_selector.models import BackendRecommendation, CircuitScore

__all__ = [
    "BackendSelector",
    "BackendRecommendation",
    "CircuitScore",
    # Advanced components
    "CircuitScorer",
]

try:
    __version__ = version("enhanced-quantum-backend-selector")
except PackageNotFoundError:  # pragma: no cover - running from a source checkout
    __version__ = "0.0.0"
