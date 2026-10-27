"""Shared pytest configuration."""

from importlib.util import find_spec

# The benchmark suite needs Poetry-only dev dependencies (qiskit-device-benchmarking,
# ffsim). Skip it when they're not installed, e.g. in the pip-based CI matrix.
collect_ignore = []
if find_spec("qiskit_device_benchmarking") is None or find_spec("ffsim") is None:
    collect_ignore.append("test_benchmarks.py")
