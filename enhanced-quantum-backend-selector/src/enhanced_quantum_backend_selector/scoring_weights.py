"""
Scoring weights configuration for backend selection.

This module provides customizable weights for the multi-criteria scoring algorithm.
"""

from dataclasses import dataclass


@dataclass
class ScoringWeights:
    """
    Customizable weights for multi-criteria backend scoring.

    Each weight determines the relative importance of a scoring criterion.
    Higher weights give more influence to that criterion in the final score.

    Default weights prioritize gate fidelity while balancing other quality factors:
    - Fidelity (1.5): Highest priority - gate and readout errors directly impact results
    - Connectivity (1.0): Important - affects transpilation overhead
    - Coherence (0.8): Moderate - matters for deep circuits
    - Queue (0.4): Lower - availability is less critical than quality

    Attributes:
        gate_fidelity_weight: Weight for gate error rates (1Q, 2Q, readout).
        connectivity_weight: Weight for topology match with circuit connectivity.
        coherence_weight: Weight for T1/T2 coherence times.
        queue_weight: Weight for queue depth and availability.

    Examples:
        >>> # Use default weights
        >>> weights = ScoringWeights()
        >>> selector.rank_backends(circuit, weights=weights)

        >>> # Prioritize queue availability for quick execution
        >>> fast_weights = ScoringWeights(
        ...     gate_fidelity_weight=1.0,
        ...     connectivity_weight=0.8,
        ...     coherence_weight=0.6,
        ...     queue_weight=2.0  # Much higher than default
        ... )

        >>> # Maximize fidelity for critical circuits
        >>> precise_weights = ScoringWeights(
        ...     gate_fidelity_weight=3.0,  # Triple weight
        ...     connectivity_weight=1.5,
        ...     coherence_weight=1.5,
        ...     queue_weight=0.1
        ... )
    """

    gate_fidelity_weight: float = 1.5
    connectivity_weight: float = 1.0
    coherence_weight: float = 0.8
    queue_weight: float = 0.4

    def __post_init__(self) -> None:
        """Validate that all weights are non-negative."""
        if self.gate_fidelity_weight < 0:
            raise ValueError("gate_fidelity_weight must be non-negative")
        if self.connectivity_weight < 0:
            raise ValueError("connectivity_weight must be non-negative")
        if self.coherence_weight < 0:
            raise ValueError("coherence_weight must be non-negative")
        if self.queue_weight < 0:
            raise ValueError("queue_weight must be non-negative")
