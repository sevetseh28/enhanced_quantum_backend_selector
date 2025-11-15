<!--
SYNC IMPACT REPORT
==================
Version: 0.0.0 → 1.0.0
Date: 2025-11-15

CHANGES:
- Initial constitution creation for Enhanced Quantum Backend Selector
- Established 7 core principles for Python library development
- Defined code quality standards, testing requirements, and CI/CD policies
- Set governance rules for compliance and amendments

PRINCIPLES ESTABLISHED:
1. Strong Typing (NON-NEGOTIABLE)
2. Comprehensive Testing & CI/CD
3. Semantic Versioning
4. Code Formatting & Style
5. Extensive Documentation
6. Code Simplicity (added: one class per file, dedicated model modules)
7. Provider Agnostic Design

TEMPLATES UPDATED:
✅ Constitution created from template

FOLLOW-UP ACTIONS:
- Verify spec.md and plan.md align with constitution principles
- Ensure task templates reference testing and typing requirements
- Update CI/CD workflows to enforce quality gates
- Verify CI/CD workflows use or mirror devcontainer configuration
- Ensure devcontainer.json is kept synchronized with pyproject.toml Python version
-->

# Enhanced Quantum Backend Selector - Constitution

## Core Principles

### I. Strong Typing (NON-NEGOTIABLE)

**All code MUST use Python type hints comprehensively.**

- Every function, method, and class attribute MUST have explicit type annotations
- Use `typing` module for complex types (Optional, Union, List, Dict, Callable, etc.)
- Type checking with mypy MUST pass with `--strict` mode before merging
- Generic types MUST be properly parameterized (e.g., `List[BackendV2]` not `List`)
- Return types MUST be explicit, including `None` when applicable
- No use of `Any` type unless absolutely justified with inline comment explaining why

**Rationale:** Type safety prevents runtime errors, improves IDE support, enables better refactoring, and serves as inline documentation. In scientific computing libraries like this, type errors can lead to incorrect quantum circuit analysis.

### II. Comprehensive Testing & CI/CD

**All code MUST have automated tests run in CI/CD pipelines.**

- Unit test coverage MUST be ≥80% (enforced in CI)
- Every public API method MUST have at least one test case
- Edge cases and error conditions MUST be tested explicitly
- Tests MUST run on every push and pull request via GitHub Actions
- Test matrix MUST include Python 3.12 and 3.13
- Integration tests MUST verify compatibility with Qiskit Aer and fake backends
- CI MUST fail if any test fails or coverage drops below threshold
- Examples in documentation MUST be validated automatically

**Rationale:** Automated testing ensures reliability, prevents regressions, and builds confidence for users integrating this library into their quantum computing workflows.

### III. Semantic Versioning

**Version numbers MUST follow semantic versioning (MAJOR.MINOR.PATCH).**

- MAJOR: Increment for breaking API changes (incompatible with previous versions)
- MINOR: Increment for new features that are backward compatible
- PATCH: Increment for bug fixes and non-functional changes
- Pre-release versions MAY use suffixes (e.g., 1.0.0-alpha.1, 1.0.0-rc.2)
- Version MUST be managed via git tags and poetry-dynamic-versioning
- CHANGELOG.md MUST be updated with every release documenting changes
- Breaking changes MUST be clearly documented with migration guides

**Rationale:** Semantic versioning provides clear expectations for users about compatibility and allows safe dependency management in downstream projects.

### IV. Code Formatting & Style

**Code MUST adhere to consistent formatting enforced by automated tools.**

- Use Ruff for linting and formatting (replaces black, isort, flake8)
- Maximum line length: 100 characters
- Import organization: standard library → third-party → local (automatically sorted)
- Pre-commit hooks MUST be configured and run before commits
- Docstrings MUST follow Google or NumPy style consistently
- Class and function names MUST follow PEP 8 conventions
- No trailing whitespace or missing newlines at end of files

**Rationale:** Consistent formatting improves readability, reduces cognitive load, eliminates style debates, and enables automatic code review focusing on logic rather than style.

### V. Extensive Documentation

**Every public API element MUST have comprehensive docstrings.**

- All public modules, classes, methods, and functions MUST have docstrings
- Docstrings MUST include: description, parameters (with types), return values, raises, examples
- Complex algorithms MUST have explanatory comments
- Type hints MUST be duplicated in docstring parameter documentation
- User-facing documentation MUST include getting started guide, API reference, and examples
- Architecture decisions MUST be documented in design docs
- CHANGELOG.md MUST track all user-facing changes

**Example Required Format:**
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
        weights: Custom scoring weights for criteria. If None, uses defaults
            (fidelity=1.5, connectivity=1.0, coherence=0.8, queue=0.4).

    Returns:
        List of BackendRecommendation objects sorted by score (highest first).
        Each recommendation includes backend reference, scores, and rank.

    Raises:
        ValueError: If circuit is empty or has no operations.

    Examples:
        >>> selector = BackendSelector(backends)
        >>> ranked = selector.rank_backends(my_circuit)
        >>> best_backend = ranked[0].backend
    """
```

**Rationale:** Documentation is critical for library adoption. Users need clear guidance on how to use the API. Docstrings serve as inline reference and enable auto-generated documentation sites.

### VI. Code Simplicity

**Functions MUST be simple, focused, and avoid unnecessary complexity.**

- Each function SHOULD do one thing and do it well (Single Responsibility Principle)
- Cyclomatic complexity SHOULD NOT exceed 10 per function
- Nesting depth MUST NOT exceed 3 levels (avoid nested if/for/while statements)
- Use early returns to reduce nesting instead of else blocks
- Extract complex conditionals into well-named boolean variables or helper methods
- Prefer guard clauses at function start for validation
- Functions longer than 50 lines SHOULD be refactored into smaller functions
- Use descriptive variable names that explain intent
- One class per file (exceptions: small related helper classes < 20 lines)
- Data classes (dataclasses, Pydantic models) MUST be separated in dedicated `models.py` modules
- File names MUST match the primary class name in snake_case (e.g., `backend_selector.py` contains `BackendSelector`)

**Anti-patterns to AVOID:**
```python
# BAD: Nested ifs
if backend.operational:
    if backend.num_qubits >= required:
        if backend.has_gate(gate_name):
            if queue_depth < threshold:
                return True
return False

# GOOD: Early returns
if not backend.operational:
    return False
if backend.num_qubits < required:
    return False
if not backend.has_gate(gate_name):
    return False
return queue_depth < threshold

# BAD: Multiple classes in one file
# File: backend_stuff.py
class BackendSelector: ...
class BackendAnalyzer: ...
class BackendMetrics: ...

# GOOD: One class per file
# File: backend_selector.py
class BackendSelector: ...

# File: backend_analyzer.py
class BackendAnalyzer: ...

# File: models.py (for data classes)
@dataclass
class BackendMetrics: ...

@dataclass
class CircuitScore: ...

@dataclass
class BackendRecommendation: ...
```

**Rationale:** Simple code is easier to understand, test, debug, and maintain. Complexity is the enemy of reliability. Scientific libraries must be correct above all else. One class per file improves navigability, reduces merge conflicts, and enforces focused responsibility. Dedicated model modules create clear separation between data structures and business logic.

### VII. Provider Agnostic Design

**The library MUST work with any Qiskit BackendV2 provider.**

- All backend interactions MUST go through the BackendV2 interface and Target class
- MUST NOT depend on provider-specific implementations (IBM, AWS, etc.)
- MUST handle missing calibration data gracefully (not all providers supply all metrics)
- Test suite MUST validate against multiple backend types (Aer, Fake, IBM)
- No hardcoded assumptions about backend behavior beyond BackendV2 contract
- Backend-specific optimizations MAY be added but MUST NOT break other providers

**Rationale:** Provider independence ensures the library remains useful as the quantum computing ecosystem evolves and new providers emerge.

## Code Quality Standards

### Type Checking Configuration
```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
```

### Testing Standards
- Use pytest as test framework
- Test files MUST mirror source structure (`test_backend_selector.py` for `backend_selector.py`)
- Use fixtures for common test setup
- Mock external dependencies (Qiskit backends) in unit tests
- Use Aer and fake backends for integration tests
- Parametrize tests for multiple scenarios when applicable
- Assert error messages, not just exceptions raised

### Linting Configuration
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "A", "C4", "PT"]
ignore = []
```

## CI/CD Requirements

### Required GitHub Actions Workflows

**1. Test Workflow (`.github/workflows/test.yml`)**
- Trigger: Every push and pull request
- Run on Python 3.12 and 3.13
- Execute: ruff linting → mypy type checking → pytest with coverage
- Upload coverage to Codecov
- Fail if coverage < 80% or any check fails
- MUST use devcontainer for consistency with local development environment

**2. Documentation Workflow (`.github/workflows/docs.yml`)**
- Trigger: Push to main branch
- Build documentation site with MkDocs Material
- Deploy to GitHub Pages
- Validate all code examples execute successfully

**3. Publish Workflow (`.github/workflows/publish.yml`)**
- Trigger: GitHub release created
- Build package with poetry
- Run full test suite one final time
- Publish to PyPI using trusted publishing or API token
- Create git tag matching release version

### Development Environment Consistency

**DevContainer MUST be the single source of truth for development environment:**
- `.devcontainer/devcontainer.json` defines Python version, extensions, system dependencies
- CI/CD workflows SHOULD use devcontainer or mirror its configuration exactly
- All team members MUST use devcontainer for local development to ensure consistency
- System dependencies (graphviz, etc.) MUST be specified in devcontainer.json
- Python version in CI matrix MUST match devcontainer Python version
- Any environment changes MUST be updated in devcontainer.json first, then propagated to CI

**DevContainer Requirements:**
- Keep Python version synchronized with `pyproject.toml` `requires-python`
- Include all VS Code extensions needed for development (Python, Jupyter, linters)
- Install system dependencies via `postCreateCommand`
- Use poetry feature for dependency management
- Document any manual setup steps in comments

### Pre-commit Hooks Required
- ruff format and lint
- mypy type checking
- trailing whitespace removal
- YAML validation
- large file check

## Governance

**This constitution supersedes all other development practices and preferences.**

### Compliance
- All pull requests MUST pass CI/CD quality gates before merging
- Code reviews MUST verify adherence to principles (typing, testing, simplicity)
- Violations of NON-NEGOTIABLE principles result in automatic PR rejection
- Exceptions require explicit justification and approval in PR discussion
- Development environment changes MUST update `.devcontainer/devcontainer.json` and be reflected in CI/CD workflows

### Amendment Process
1. Propose amendment with rationale in GitHub issue
2. Demonstrate impact analysis on existing code
3. Require consensus from maintainers
4. Document amendment in constitution with version bump (MINOR)
5. Update dependent artifacts (templates, CI configs)
6. Provide migration period for breaking changes

### Version History
- Version changes follow semantic versioning
- MAJOR: Removal or fundamental change of core principle
- MINOR: Addition of new principle or section
- PATCH: Clarifications, typo fixes, non-semantic updates

**Version**: 1.0.0 | **Ratified**: 2025-11-15 | **Last Amended**: 2025-11-15
