# Release Process Documentation

This document describes the automated release and publishing process for the Enhanced Quantum Backend Selector project.

## Overview

This project uses **automated semantic versioning** and **continuous deployment** to PyPI. Releases are created automatically when commits are merged to the `main` branch, based on conventional commit messages.

### Key Technologies

- **[Poetry](https://python-poetry.org/)**: Dependency management and package building
- **[python-semantic-release](https://python-semantic-release.readthedocs.io/)**: Actually we use Node.js semantic-release for version management
- **[Conventional Commits](https://www.conventionalcommits.org/)**: Commit message format for automatic versioning
- **[GitHub Actions](https://docs.github.com/en/actions)**: CI/CD automation
- **[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)**: Secure, token-less publishing

## Automated Release Workflow

### 1. How Releases Are Triggered

Releases are **automatically created** when code is merged to the `main` branch. The workflow:

1. Analyzes commit messages since the last release
2. Determines the next version number based on conventional commits
3. Updates `pyproject.toml` with the new version
4. Generates/updates `CHANGELOG.md`
5. Creates a Git tag and GitHub Release
6. Attaches build artifacts (`.whl` and `.tar.gz` files)

### 2. Version Determination

Version increments follow [Semantic Versioning](https://semver.org/) based on commit types:

| Commit Type | Version Bump | Example |
|-------------|--------------|---------|
| `feat:` | **MINOR** (0.x.0) | `feat: add caching support` → 0.2.0 |
| `fix:` | **PATCH** (0.0.x) | `fix: handle missing calibration data` → 0.1.1 |
| `perf:` | **PATCH** (0.0.x) | `perf: optimize transpilation` → 0.1.1 |
| `BREAKING CHANGE:` | **MAJOR** (x.0.0) | `feat!: redesign API` → 1.0.0 |
| `docs:`, `refactor:` | **PATCH** (0.0.x) | `docs: update README` → 0.1.1 |
| `chore:`, `test:`, `ci:` | **NO RELEASE** | `chore: update dependencies` (no release) |

**Note**: Breaking changes can be indicated by:
- Adding `!` after the type: `feat!: new API`
- Including `BREAKING CHANGE:` in the commit footer

### 3. Commit Message Format

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Examples:**

```bash
# New feature (bumps minor version)
git commit -m "feat(selector): add support for dynamic circuit analysis"

# Bug fix (bumps patch version)
git commit -m "fix(scorer): correct error rate calculation for idle qubits"

# Performance improvement (bumps patch version)
git commit -m "perf(cache): reduce memory footprint of backend cache"

# Breaking change (bumps major version)
git commit -m "feat(api)!: redesign BackendSelector initialization

BREAKING CHANGE: BackendSelector now requires explicit backend list"

# Documentation (bumps patch version)
git commit -m "docs(readme): add installation troubleshooting section"

# No release
git commit -m "chore(deps): update qiskit to 2.2.4"
git commit -m "test(integration): add more canonical circuit tests"
```

**Common Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Common Scopes:**
- `selector`: BackendSelector class
- `scorer`: Scoring system
- `cache`: Caching functionality
- `api`: Public API
- `docs`: Documentation
- `deps`: Dependencies

## PyPI Publishing Workflow

### 1. Automatic Publishing

After a successful release, the **Publish to PyPI** workflow automatically:

1. Checks out the tagged release
2. Runs tests to ensure quality
3. Builds the package using Poetry (`poetry build`)
4. Validates the distribution with `twine check`
5. Publishes to PyPI using [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

### 2. TestPyPI for Testing

You can manually test the publishing process using TestPyPI:

1. Go to **Actions** → **Publish to PyPI**
2. Click **Run workflow**
3. Select branch
4. Set "Publish to TestPyPI instead of PyPI" to **true**
5. Click **Run workflow**

This will publish to https://test.pypi.org/project/enhanced-quantum-backend-selector/

### 3. Manual Publishing (Emergency Only)

If automatic publishing fails, maintainers can manually publish:

```bash
# Ensure you're on the tagged release
git checkout v0.1.0

# Navigate to package directory
cd enhanced-quantum-backend-selector

# Build the package
poetry build

# Check distribution
poetry run twine check dist/*

# Publish to TestPyPI first (test)
poetry publish -r testpypi

# If successful, publish to PyPI
poetry publish
```

**Note**: Manual publishing requires PyPI API token configured in `~/.pypirc` or via environment variables.

## Required GitHub Secrets and Configuration

### GitHub Secrets

Configure these secrets in **Settings** → **Secrets and variables** → **Actions**:

| Secret Name | Required | Description | How to Get |
|-------------|----------|-------------|------------|
| `CODECOV_TOKEN` | Optional | Code coverage reporting | [codecov.io](https://codecov.io/) → Repository Settings |
| `PYPI_API_TOKEN` | No* | PyPI publishing (legacy) | [pypi.org](https://pypi.org/manage/account/token/) → Account Settings → API Tokens |
| `TEST_PYPI_API_TOKEN` | No* | TestPyPI publishing (legacy) | [test.pypi.org](https://test.pypi.org/manage/account/token/) |

***Note**: Not required when using Trusted Publishing (recommended approach)

### GitHub Environments

Create these environments in **Settings** → **Environments**:

#### `pypi` Environment
- **Deployment protection rules**: Recommended - require approval for production
- **Environment secrets**: None needed with Trusted Publishing
- **Trusted Publishing**: Configured on PyPI (see below)

#### `testpypi` Environment
- **Deployment protection rules**: None needed
- **Environment secrets**: None needed with Trusted Publishing
- **Trusted Publishing**: Configured on TestPyPI (see below)

### PyPI Trusted Publishing Setup

Trusted Publishing is the **recommended** and most secure method. No API tokens needed!

#### On PyPI:
1. Go to https://pypi.org/manage/account/publishing/
2. Click **Add a new pending publisher**
3. Fill in:
   - **PyPI Project Name**: `enhanced-quantum-backend-selector`
   - **Owner**: `sevetseh28`
   - **Repository**: `enhanced_quantum_backend_selector`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click **Add**

#### On TestPyPI:
1. Go to https://test.pypi.org/manage/account/publishing/
2. Click **Add a new pending publisher**
3. Fill in:
   - **PyPI Project Name**: `enhanced-quantum-backend-selector`
   - **Owner**: `sevetseh28`
   - **Repository**: `enhanced_quantum_backend_selector`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `testpypi`
4. Click **Add**

**First-time publishing**: For the initial publish, you may need to:
1. Manually create the project on PyPI/TestPyPI, OR
2. Use API token for the first release, then configure Trusted Publishing

### GitHub Branch Protection

Configure branch protection for `main` in **Settings** → **Branches**:

- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
  - Required checks: `test`, `build`
- ✅ Require branches to be up to date before merging
- ✅ Include administrators (recommended)

## Workflow Files

### `.github/workflows/test.yml`
- **Trigger**: Push/PR to `main` or `develop`
- **Purpose**: Run tests, linting, type checking, coverage
- **Matrix**: Python 3.12 and 3.13
- **Artifacts**: Coverage reports

### `.github/workflows/release.yml`
- **Trigger**: Push to `main` branch
- **Purpose**: Create semantic releases
- **Steps**:
  1. Run tests and build
  2. Analyze commits for version
  3. Update `pyproject.toml` version
  4. Generate/update `CHANGELOG.md`
  5. Create Git tag and GitHub Release
  6. Upload build artifacts to release

### `.github/workflows/publish.yml`
- **Trigger**: Release published, version tags, manual dispatch
- **Purpose**: Publish to PyPI/TestPyPI
- **Steps**:
  1. Run tests
  2. Build package with Poetry
  3. Validate with twine
  4. Publish using Trusted Publishing

### `.github/workflows/docs.yml`
- **Trigger**: Push/PR to `main`, manual dispatch
- **Purpose**: Build and deploy documentation
- **Deployment**: GitHub Pages at https://sevetseh28.github.io/enhanced_quantum_backend_selector

## Configuration Files

### `.releaserc.json`
Semantic-release configuration:
- **Branches**: Only `main` triggers releases
- **Plugins**:
  - `@semantic-release/commit-analyzer`: Determines version bump
  - `@semantic-release/release-notes-generator`: Generates release notes
  - `@semantic-release/changelog`: Updates CHANGELOG.md
  - `@semantic-release/exec`: Runs `poetry version` command
  - `@semantic-release/git`: Commits version and changelog
  - `@semantic-release/github`: Creates GitHub Release

### `pyproject.toml`
Poetry and project configuration:
- **Version**: Managed by semantic-release via `poetry version`
- **Build system**: `poetry-core`
- **Dependencies**: Managed by Poetry
- **Dev tools**: pytest, mypy, ruff, pre-commit

## Testing the Release Process

### 1. Test on a Feature Branch

Create a test branch with conventional commits:

```bash
git checkout -b test/release-workflow
echo "# Test" >> TEST.md
git add TEST.md
git commit -m "feat(test): add test feature for release workflow"
git push origin test/release-workflow
```

Create a PR and observe the test workflow.

### 2. Dry-run Semantic Release Locally

```bash
# Install semantic-release dependencies
npm install -g \
  semantic-release@23 \
  @semantic-release/changelog@6 \
  @semantic-release/exec@6 \
  @semantic-release/git@10 \
  @semantic-release/github@10 \
  conventional-changelog-conventionalcommits@7

# Run dry-run (does not publish)
npx semantic-release --dry-run
```

This shows what version would be released without actually creating it.

### 3. Test PyPI Publishing

Use TestPyPI for safe testing:

1. Configure TestPyPI Trusted Publishing (see above)
2. Trigger manual workflow with TestPyPI option
3. Verify package at https://test.pypi.org/project/enhanced-quantum-backend-selector/
4. Test installation:
   ```bash
   pip install -i https://test.pypi.org/simple/ enhanced-quantum-backend-selector
   ```

## Monitoring and Troubleshooting

### Check Workflow Status

- **Actions Tab**: https://github.com/sevetseh28/enhanced_quantum_backend_selector/actions
- **Release workflow**: Look for "Automated Release" runs
- **Publish workflow**: Look for "Publish to PyPI" runs

### Common Issues

#### No Release Created
**Symptoms**: Commits merged to main, but no release
**Causes**:
- Commits don't follow conventional format
- Commit types that don't trigger releases (`chore`, `test`, `ci`)
- No commits since last release

**Solution**: Ensure commits use proper conventional format with release-triggering types

#### Release Created but No PyPI Publish
**Symptoms**: GitHub Release exists, but package not on PyPI
**Causes**:
- Publish workflow failed
- Trusted Publishing not configured
- Tests failing in publish workflow

**Solution**:
1. Check publish workflow logs
2. Verify Trusted Publishing setup
3. Manually trigger publish workflow if needed

#### Build Failures
**Symptoms**: Workflows fail during build step
**Causes**:
- Poetry dependencies not resolving
- Test failures
- Linting/type checking errors

**Solution**:
1. Ensure local `poetry install` works
2. Run `poetry run pytest` locally
3. Fix any linting/type errors before merging

#### Version Conflicts
**Symptoms**: semantic-release complains about existing version
**Causes**:
- Manual version edits in pyproject.toml
- Re-running release for same commits

**Solution**:
- Never manually edit version in pyproject.toml
- Let semantic-release manage versions
- Delete problematic tags if needed: `git tag -d v0.1.0 && git push origin :refs/tags/v0.1.0`

### Viewing Logs

```bash
# View workflow runs
gh run list --workflow=release.yml

# View specific run logs
gh run view <run-id> --log

# View failed run
gh run view <run-id> --log-failed
```

## Maintainer Checklist

Before merging to `main`:

- [ ] All commits follow conventional commit format
- [ ] CHANGELOG.md has `[Unreleased]` section with changes
- [ ] Tests pass locally: `poetry run pytest`
- [ ] Linting passes: `poetry run ruff check .`
- [ ] Type checking passes: `poetry run mypy src/`
- [ ] Documentation updated if needed
- [ ] PR approved and all CI checks green

After merge to `main`:

- [ ] Monitor release workflow execution
- [ ] Verify GitHub Release created with correct version
- [ ] Verify CHANGELOG.md updated
- [ ] Verify pyproject.toml version updated
- [ ] Check publish workflow execution
- [ ] Verify package appears on PyPI
- [ ] Test installation: `pip install enhanced-quantum-backend-selector`
- [ ] Announce release (if significant)

## Emergency Procedures

### Rollback a Bad Release

If a critical bug is found in a release:

1. **Do NOT delete the release or tag** (breaks semantic versioning)
2. **Create a fix**:
   ```bash
   git checkout -b fix/critical-bug
   # Make fixes
   git commit -m "fix: critical bug in backend selection"
   ```
3. **Merge fix to main** - this will create a patch release automatically
4. **If needed**, mark the bad release as "pre-release" on GitHub

### Manual Hotfix Process

For urgent fixes that can't wait for normal release:

1. Create fix on `main`
2. Manually create and push tag:
   ```bash
   git tag -a v0.1.1 -m "Hotfix: critical bug fix"
   git push origin v0.1.1
   ```
3. Publish workflow will trigger automatically

## Release History

View all releases: https://github.com/sevetseh28/enhanced_quantum_backend_selector/releases

View CHANGELOG: [CHANGELOG.md](CHANGELOG.md)

View on PyPI: https://pypi.org/project/enhanced-quantum-backend-selector/

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Semantic Release Documentation](https://semantic-release.gitbook.io/semantic-release/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Questions or Issues?

If you have questions about the release process:
1. Check this documentation
2. Review workflow logs in GitHub Actions
3. Open an issue on GitHub
4. Contact repository maintainers

---

**Last Updated**: December 2025
**Maintained By**: @sevetseh28
