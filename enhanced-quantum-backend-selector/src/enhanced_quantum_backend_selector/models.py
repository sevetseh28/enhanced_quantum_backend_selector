"""
Data models for backend analysis and circuit scoring.

This module contains dataclasses used throughout the enhanced quantum backend selector.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BackendMetrics:
    """Dataclass for backend metrics with comprehensive performance information"""
    # Basic properties
    name: str = ""
    num_qubits: Optional[int] = None
    max_circuits: Optional[int] = None
    
    # Operations
    num_operations: int = 0
    operations: List[str] = field(default_factory=list)
    
    # Single-qubit gate errors
    avg_1q_error: Optional[float] = None
    max_1q_error: Optional[float] = None
    min_1q_error: Optional[float] = None
    
    # Two-qubit gate errors
    avg_2q_error: Optional[float] = None
    max_2q_error: Optional[float] = None
    min_2q_error: Optional[float] = None
    
    # Readout errors
    avg_readout_error: Optional[float] = None
    max_readout_error: Optional[float] = None
    
    # Coherence times
    avg_t1: Optional[float] = None
    min_t1: Optional[float] = None
    max_t1: Optional[float] = None
    avg_t2: Optional[float] = None
    min_t2: Optional[float] = None
    
    # Connectivity
    num_edges: Optional[int] = None
    is_bidirectional: Optional[bool] = None
    connectivity_ratio: Optional[float] = None
    avg_degree: Optional[float] = None
    
    # Status
    operational: Optional[bool] = None
    pending_jobs: Optional[int] = None


@dataclass
class CircuitScore:
    """Dataclass for circuit scoring results"""
    backend: str
    compatible: bool
    reasons: List[str] = field(default_factory=list)
    score: float = 100.0
