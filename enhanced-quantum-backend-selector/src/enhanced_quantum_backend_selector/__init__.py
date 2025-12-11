"""
Enhanced Quantum Backend Selector

A library for intelligent quantum backend selection using multiple criteria.
"""

from enhanced_quantum_backend_selector.backend_selector import BackendSelector

# Keep exploration components available for advanced users
from enhanced_quantum_backend_selector.exploration.backend_analyzer import (
    BackendAnalyzer,
)
from enhanced_quantum_backend_selector.exploration.circuit_scorer import (
    CircuitScorer,
)
from enhanced_quantum_backend_selector.models import (
    AggregatedScore,
    BackendMetrics,
    BackendRecommendation,
    CircuitScore,
    ScoringConfiguration,
    TranspilationRun,
)
from enhanced_quantum_backend_selector.scoring_weights import ScoringWeights

__all__ = [
    "BackendSelector",
    "BackendRecommendation",
    "ScoringWeights",
    "BackendMetrics",
    "CircuitScore",
    "ScoringConfiguration",
    "AggregatedScore",
    "TranspilationRun",
    # Exploration/internal components
    "BackendAnalyzer",
    "CircuitScorer",
]

__version__ = "0.1.0"
