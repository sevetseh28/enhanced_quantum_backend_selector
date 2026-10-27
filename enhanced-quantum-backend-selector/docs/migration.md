# Migrating from 0.1 to 1.0

Version 1.0 changes what the score means and how unusable backends are reported. Most
code needs only its thresholds and error calculations updated.

## Scores are success probabilities

In 0.1 the score was the negative sum of the error rates, so it was unbounded below and
deep circuits could score `-5.0` ("500% error"). In 1.0 the score is the estimated
probability that the circuit runs without error, between 0 and 1. It includes gate,
readout and idle (T1/T2) error.

| | 0.1 | 1.0 |
|---|---|---|
| Perfect backend | `0` | `1.0` |
| 2% expected error | about `-0.02` | `0.98` |
| Higher is better | yes | yes |

Update thresholds and error calculations:

```python
# 0.1
rec = selector.select_backend(qc, min_score=-0.05)
error_pct = -rec.score_data.score * 100

# 1.0
rec = selector.select_backend(qc, min_score=0.95)  # at least 95% success
error_pct = (1 - rec.score_data.score) * 100
```

Backends are ranked by the new `CircuitScore.log_success_probability` field, the natural
log of the score, which keeps very deep circuits apart when every score underflows to 0.
`CircuitScore.score` now defaults to `1.0` instead of `100`.

## Incompatible backends are returned, not dropped

`rank_backends()` now returns every backend. Backends that can't run the circuit (too few
qubits, not operational, or transpilation failed) come last with `compatible=False`, a
score of `0` and the reason in `score_data.reasons`. In 0.1 a backend that failed to
transpile was dropped with a printed warning; it is now logged with `logging`.

If you only want usable backends:

```python
usable = [r for r in selector.rank_backends(qc) if r.score_data.compatible]
```

`select_backend()` still only returns compatible backends by default.

## Removed APIs

- `BackendAnalyzer` was removed. Use `CircuitScorer` to score a transpiled circuit on one
  backend.
- `BackendSelector.clear_cache()` was removed. Backend data is no longer cached, so every
  call uses the backend's current calibration.

## New in 1.0

- `BackendSelector(backends, seed=...)` makes transpilation, and therefore scores,
  reproducible.
- Idle error from each qubit's T1/T2 is part of the score.
- The package ships type information (`py.typed`).
- Qiskit 2.2.0 or later is required (0.1 required 2.2.3).
