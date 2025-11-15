# Contributing to Enhanced Quantum Backend Selector

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.12 or 3.13
- Poetry (for dependency management)
- Git

### Getting Started

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/enhanced_quantum_backend_selector.git
cd enhanced_quantum_backend_selector/enhanced-quantum-backend-selector
```

2. **Install dependencies**

```bash
poetry install --with dev,docs
```

3. **Install pre-commit hooks**

```bash
poetry run pre-commit install
```

4. **Run tests to verify setup**

```bash
poetry run pytest
```

## Development Workflow

### Code Style

This project follows strict code quality standards enforced by automated tools:

- **Formatting**: Ruff (100 character line limit)
- **Linting**: Ruff with comprehensive rule set (E, F, I, N, W, UP, B, A, C4, PT)
- **Type Checking**: mypy in strict mode
- **Testing**: pytest with minimum 80% coverage

All checks run automatically via pre-commit hooks before each commit.

### Constitution Principles

Please review `.specify/memory/constitution.md` for project principles including:

1. **Strong Typing** (NON-NEGOTIABLE): All code must have comprehensive type hints
2. **Code Simplicity**: Max 3-level nesting, one class per file, early returns over nested ifs
3. **Comprehensive Documentation**: All public APIs must have Google-style docstrings with examples
4. **Testing**: >80% coverage required

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/test_backend_selector.py

# Run with verbose output
poetry run pytest -v
```

### Type Checking

```bash
# Run mypy on entire codebase
poetry run mypy src/

# Check specific file
poetry run mypy src/enhanced_quantum_backend_selector/backend_selector.py
```

### Linting and Formatting

```bash
# Auto-format code
poetry run ruff format .

# Run linter
poetry run ruff check .

# Auto-fix linting issues
poetry run ruff check --fix .
```

## Making Changes

### Branch Naming

- Feature branches: `feature/your-feature-name`
- Bug fixes: `fix/bug-description`
- Documentation: `docs/what-you-are-documenting`

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(selector): add caching support for backend metrics
fix(scorer): handle missing calibration data gracefully
docs(readme): add installation instructions
test(canonical): add GHZ circuit validation tests
```

### Pull Request Process

1. **Create a branch** from `main`
2. **Make your changes** following code style and principles
3. **Add tests** for new functionality (maintain >80% coverage)
4. **Update documentation** as needed
5. **Run all checks**:
   ```bash
   poetry run pre-commit run --all-files
   poetry run pytest
   poetry run mypy src/
   ```
6. **Push your branch** and create a Pull Request
7. **Address review feedback** promptly
8. **Ensure CI passes** before merging

### Pull Request Checklist

- [ ] Code follows project style (ruff, mypy passing)
- [ ] All new code has type hints
- [ ] Comprehensive docstrings added
- [ ] Tests added/updated (coverage >80%)
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] Pre-commit hooks passing
- [ ] All CI checks passing

## Code Review Standards

Reviewers will check for:

- Compliance with constitution principles
- Type safety (strict mypy compliance)
- Test coverage and quality
- Documentation completeness
- Code simplicity (avoid complexity)
- API design consistency

## Testing Guidelines

### Unit Tests

- Test individual functions and methods
- Use mocks for external dependencies
- Test edge cases and error conditions
- Assert error messages, not just exceptions

### Integration Tests

- Test end-to-end workflows
- Use Qiskit Aer and fake backends
- Validate multi-component interactions

### Canonical Circuit Tests

- Verify recommendations for standard quantum circuits (GHZ, QFT, VQE)
- Compare against `least_busy()` baseline
- Ensure measurable improvements

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def rank_backends(
    self,
    circuit: QuantumCircuit,
    weights: Optional[ScoringWeights] = None,
) -> List[BackendRecommendation]:
    """
    Rank all backends for a given quantum circuit.

    Analyzes each backend against circuit requirements using multi-criteria
    scoring. Backends are sorted by total score in descending order.

    Args:
        circuit: The quantum circuit to analyze and match against backends.
        weights: Custom scoring weights. If None, uses defaults.

    Returns:
        List of BackendRecommendation objects sorted by score (highest first).

    Raises:
        ValueError: If circuit is empty or has no operations.

    Examples:
        >>> selector = BackendSelector(backends)
        >>> ranked = selector.rank_backends(my_circuit)
        >>> best_backend = ranked[0].backend
    """
```

### Building Documentation

```bash
# Build documentation locally
poetry run mkdocs build

# Serve documentation with live reload
poetry run mkdocs serve
```

## Release Process

Only maintainers can create releases:

1. Update CHANGELOG.md with release version and date
2. Commit changes to `main`
3. Create annotated git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. Create GitHub Release from tag
6. GitHub Actions automatically publishes to PyPI

## Getting Help

- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: See docs/ directory or https://sevetseh28.github.io/enhanced_quantum_backend_selector

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help newcomers get started

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
