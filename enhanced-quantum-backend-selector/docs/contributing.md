# Contributing

Thank you for your interest in contributing!

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/enhanced_quantum_backend_selector.git
cd enhanced-quantum-backend-selector/enhanced-quantum-backend-selector
```

### 2. Set Up Development Environment

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --with dev,docs

# Install pre-commit hooks
poetry run pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Code Quality Standards

### Type Safety

All code must be fully typed with mypy strict mode:

```python
def analyze_backend(backend: BackendV2) -> dict[str, float]:
    metrics: dict[str, float] = {}
    return metrics
```

```bash
poetry run mypy src/
```

### Code Formatting

```bash
poetry run ruff format .
```

### Linting

```bash
poetry run ruff check .
poetry run ruff check --fix .  # Auto-fix
```

### Testing

Minimum 80% code coverage required:

```bash
poetry run pytest
poetry run pytest --cov --cov-report=term-missing
```

## Documentation

Use Google-style docstrings:

```python
def select_backend(self, circuit: QuantumCircuit) -> BackendRecommendation:
    """Select the best backend for a quantum circuit.

    Args:
        circuit: The quantum circuit to execute.

    Returns:
        BackendRecommendation with selected backend and scoring info.

    Raises:
        ValueError: If no compatible backends found.
    """
```

## Project Structure

```
enhanced-quantum-backend-selector/
├── src/enhanced_quantum_backend_selector/
│   ├── __init__.py
│   ├── backend_selector.py
│   ├── circuit_scorer.py
│   └── models.py
├── tests/
├── examples/
├── docs/
└── pyproject.toml
```

## Making Changes

### Adding a Feature

1. Write tests first
2. Implement the feature
3. Add documentation
4. Run quality checks

### Fixing a Bug

1. Write a failing test
2. Fix the bug
3. Verify test passes

## Pull Request Process

Before submitting:

- [ ] All tests pass
- [ ] Coverage ≥80%
- [ ] mypy passes
- [ ] Ruff formatting and linting pass
- [ ] Pre-commit hooks pass
- [ ] Documentation updated

## Development Commands

```bash
# Run tests
poetry run pytest -v

# Type checking
poetry run mypy src/

# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .

# Build docs locally
poetry run mkdocs serve
```

## Getting Help

- **Issues:** Open an issue on GitHub
- **Documentation:** Check the [User Guide](user-guide.md)

Thank you for contributing! 🎉
