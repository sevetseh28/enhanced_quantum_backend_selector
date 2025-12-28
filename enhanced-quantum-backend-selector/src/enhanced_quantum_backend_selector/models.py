"""
Data models for backend analysis and circuit scoring.

This module contains dataclasses used throughout the enhanced quantum backend selector.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qiskit.providers import BackendV2

# Operations to skip when calculating gate errors.
# These operations do not contribute to gate-based errors:
# - "measure": Measurement errors are modeled separately from gate errors.
# - "delay": Delays are not physical gates and have distinct error models (e.g., decoherence).
# - "reset": Reset operations are handled separately and have their own error characteristics.
# Only gate operations are considered when aggregating gate error metrics.
SKIP_OPERATIONS = frozenset(["measure", "delay", "reset"])


@dataclass
class CircuitScore:
    """
    Circuit scoring results for a specific backend.

    Attributes:
        backend: Name of the backend that was scored.
        compatible: Whether the backend is compatible with the circuit.
        reasons: List of human-readable reasons explaining the score.
        score: Overall score (0-100), higher is better.
    """

    backend: str
    compatible: bool
    reasons: list[str] = field(default_factory=list)
    score: float = 100.0


@dataclass
class BackendRecommendation:
    """
    Complete recommendation for a backend including reference and scoring details.

    This is the primary output type for backend selection, containing everything
    needed to understand why a backend was recommended.

    Attributes:
        backend: The actual BackendV2 instance.
        score_data: Detailed scoring information for the circuit.
        rank: Ranking position (1 = best, 2 = second best, etc.).

    Examples:
        >>> recommendations = selector.rank_backends(circuit)
        >>> best = recommendations[0]
        >>> print(f"Recommended: {best.backend.name} (rank {best.rank})")
        >>> print(f"Score: {best.score_data.score:.2f}")
        >>> print(f"Reasons: {', '.join(best.score_data.reasons)}")
    """

    backend: BackendV2
    score_data: CircuitScore
    rank: int
