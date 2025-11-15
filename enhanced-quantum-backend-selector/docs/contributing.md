# Contributing

Thank you for your interest in contributing to the Enhanced Quantum Backend Selector! This guide will help you get started.

## Code of Conduct

This project adheres to the following principles:

- **Be respectful**: Treat all contributors with respect
- **Be constructive**: Provide helpful feedback
- **Be collaborative**: Work together toward common goals
- **Be inclusive**: Welcome contributors of all backgrounds

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/enhanced_quantum_backend_selector.git
cd enhanced-quantum-backend-selector/enhanced-quantum-backend-selector
```

### 2. Set Up Development Environment

```bash
# Install Poetry (if not already installed)
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

## Development Workflow

### Code Quality Standards

This project enforces strict quality standards:

#### 1. Type Safety

**All code must be fully typed with mypy strict mode**:

```python
from typing import List
from qiskit.providers import BackendV2

def analyze_backend(backend: BackendV2) -> dict[str, float]:
    """Analyze backend metrics.
    
    Args:
        backend: The backend to analyze
        
    Returns:
        Dictionary of metric names to values
    """
    metrics: dict[str, float] = {}
    # Implementation
    return metrics
```

Run type checking:

```bash
poetry run mypy src/
```

#### 2. Code Formatting

**All code must be formatted with Ruff**:

```bash
# Format code
poetry run ruff format .

# Check formatting
poetry run ruff format --check .
```

#### 3. Linting

**All code must pass Ruff linting**:

```bash
# Run linter
poetry run ruff check .

# Fix auto-fixable issues
poetry run ruff check --fix .
```

#### 4. Testing

**All features must have tests with ≥80% coverage**:

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=enhanced_quantum_backend_selector --cov-report=term-missing

# Coverage must be ≥80%
```

#### 5. Documentation

**All public APIs must have Google-style docstrings**:

```python
def select_backend(
    self,
    circuit: QuantumCircuit,
    weights: ScoringWeights | None = None,
) -> BackendRecommendation:
    """Select the best backend for a quantum circuit.
    
    This method analyzes all available backends and returns the one
    with the highest composite score based on the provided weights.
    
    Args:
        circuit: The quantum circuit to execute
        weights: Optional custom scoring weights. If None, uses defaults.
        
    Returns:
        A BackendRecommendation containing the selected backend and
        detailed scoring information.
        
    Raises:
        ValueError: If no backends are available or no compatible
            backends are found.
        
    Examples:
        >>> selector = BackendSelector(backends)
        >>> rec = selector.select_backend(qc)
        >>> print(rec.backend.name)
        'ibm_brisbane'
    """
    # Implementation
```

### Running Pre-Commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Run manually
poetry run pre-commit run --all-files
```

Hooks include:
- Ruff formatting
- Ruff linting
- mypy type checking
- Trailing whitespace removal
- YAML validation
- File size limits

## Project Structure

```
enhanced-quantum-backend-selector/
├── src/
│   └── enhanced_quantum_backend_selector/
│       ├── __init__.py           # Public API exports
│       ├── backend_selector.py   # Main BackendSelector class
│       ├── scoring_weights.py    # ScoringWeights configuration
│       ├── models.py              # Data models
│       └── exploration/           # Internal analysis modules
├── tests/
│   ├── fixtures/                  # Test fixtures
│   ├── test_backend_selector.py   # Unit tests
│   ├── test_integration.py        # Integration tests
│   └── test_canonical_validation.py
├── examples/                      # Usage examples
├── docs/                          # Documentation
├── pyproject.toml                 # Project configuration
├── mkdocs.yml                     # Documentation config
└── README.md
```

## Constitution Principles

All code must adhere to these principles:

### I. Strong Typing (NON-NEGOTIABLE)

- All parameters and return values must have type annotations
- Use `mypy --strict` mode
- No `Any` types unless absolutely necessary
- Use proper generics and type variables

### II. Comprehensive Testing

- Minimum 80% code coverage
- Unit tests for all functions
- Integration tests for workflows
- Edge case testing

### III. Semantic Versioning

- MAJOR.MINOR.PATCH format
- Breaking changes increment MAJOR
- New features increment MINOR
- Bug fixes increment PATCH

### IV. Code Formatting

- Use Ruff with 100-character line limit
- Consistent style throughout codebase
- Auto-formatting via pre-commit hooks

### V. Extensive Documentation

- Google-style docstrings for all public APIs
- Examples in docstrings
- User guides for features
- Architecture documentation

### VI. Code Simplicity

- Maximum 3-level nesting
- One class per file (in dedicated modules)
- Functions should be focused and simple
- Avoid complex conditionals

### VII. Provider Agnostic

- Support any Qiskit BackendV2 provider
- No vendor-specific code
- Test with multiple backend types

## Making Changes

### Adding a New Feature

1. **Write Tests First** (TDD):
   ```python
   # tests/test_new_feature.py
   def test_new_feature():
       """Test the new feature works correctly."""
       result = new_feature(input_data)
       assert result == expected_output
   ```

2. **Implement the Feature**:
   ```python
   # src/enhanced_quantum_backend_selector/new_feature.py
   def new_feature(input_data: InputType) -> OutputType:
       """Implement the new feature.
       
       Args:
           input_data: Description
           
       Returns:
           Description
       """
       # Implementation
   ```

3. **Add Documentation**:
   - Update relevant docs in `docs/`
   - Add examples in `examples/`
   - Update `CHANGELOG.md`

4. **Run Quality Checks**:
   ```bash
   poetry run pytest
   poetry run mypy src/
   poetry run ruff check .
   poetry run ruff format --check .
   ```

### Fixing a Bug

1. **Write a Failing Test**:
   ```python
   def test_bug_reproduction():
       """Test that reproduces the bug."""
       # This should fail before the fix
       assert buggy_function() == expected_result
   ```

2. **Fix the Bug**

3. **Verify Test Passes**

4. **Update CHANGELOG.md**

## Pull Request Process

### 1. Ensure Quality

Before submitting, verify:

- [ ] All tests pass
- [ ] Coverage ≥80%
- [ ] mypy passes
- [ ] Ruff formatting passes
- [ ] Ruff linting passes
- [ ] Pre-commit hooks pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### 2. Create Pull Request

- Use a descriptive title
- Reference any related issues
- Describe the changes made
- Include examples if applicable

### 3. Code Review

- Address reviewer feedback
- Keep commits focused and atomic
- Maintain clean git history

### 4. Merge

After approval:
- Squash commits if requested
- Ensure CI passes
- Merge to main branch

## Development Tips

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_backend_selector.py

# Run specific test
poetry run pytest tests/test_backend_selector.py::test_select_backend

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run pytest --cov

# Run and show missing lines
poetry run pytest --cov --cov-report=term-missing
```

### Type Checking

```bash
# Check all files
poetry run mypy src/

# Check specific file
poetry run mypy src/enhanced_quantum_backend_selector/backend_selector.py

# Show error codes
poetry run mypy --show-error-codes src/
```

### Code Formatting

```bash
# Format all files
poetry run ruff format .

# Check formatting without changes
poetry run ruff format --check .

# Format specific file
poetry run ruff format src/enhanced_quantum_backend_selector/backend_selector.py
```

### Documentation

```bash
# Build documentation locally
poetry run mkdocs serve

# Open http://127.0.0.1:8000 in browser

# Build static site
poetry run mkdocs build
```

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions builds and publishes to PyPI

## Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check the [User Guide](user-guide.md)

## Recognition

Contributors are recognized in:
- `CHANGELOG.md` for each release
- GitHub contributor graph
- Release notes

Thank you for contributing! 🎉
