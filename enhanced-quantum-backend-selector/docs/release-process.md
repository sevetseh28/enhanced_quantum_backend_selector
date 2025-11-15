# Release Process

This document describes the release process for the Enhanced Quantum Backend Selector.

## Overview

The project uses semantic versioning (MAJOR.MINOR.PATCH) and automated release workflows via GitHub Actions.

## Version Numbering

- **MAJOR**: Breaking changes to public API
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Examples:
- `0.1.0` → `0.2.0`: New feature added
- `0.2.0` → `0.2.1`: Bug fix
- `0.2.1` → `1.0.0`: Breaking API change

## Release Workflow

### 1. Prepare the Release

**Update CHANGELOG.md**:

```markdown
## [0.2.0] - 2025-11-20

### Added
- New feature X with API endpoint Y

### Changed
- Improved performance of Z

### Fixed
- Bug in feature A

[0.2.0]: https://github.com/sevetseh28/enhanced_quantum_backend_selector/compare/v0.1.0...v0.2.0
```

**Update pyproject.toml version**:

```toml
[tool.poetry]
version = "0.2.0"
```

**Commit changes**:

```bash
git add CHANGELOG.md enhanced-quantum-backend-selector/pyproject.toml
git commit -m "chore: prepare release v0.2.0"
git push origin main
```

### 2. Create Git Tag

```bash
# Tag the release
git tag -a v0.2.0 -m "Release v0.2.0"

# Push the tag
git push origin v0.2.0
```

### 3. Create GitHub Release

1. Go to https://github.com/sevetseh28/enhanced_quantum_backend_selector/releases/new
2. Select the tag you just created (`v0.2.0`)
3. Title: `v0.2.0`
4. Description: Copy relevant section from CHANGELOG.md
5. Click "Publish release"

This triggers the `publish.yml` workflow which:
- Runs all tests
- Builds the package
- Publishes to PyPI (using trusted publishing)
- Uploads artifacts to the release

### 4. Verify Publication

**Check PyPI**:
- https://pypi.org/project/enhanced-quantum-backend-selector/

**Test installation**:

```bash
# Create clean virtual environment
python -m venv test-env
source test-env/bin/activate

# Install from PyPI
pip install enhanced-quantum-backend-selector==0.2.0

# Test import
python -c "from enhanced_quantum_backend_selector import BackendSelector; print('Success!')"

# Cleanup
deactivate
rm -rf test-env
```

## Testing Releases

### Test on TestPyPI First

Before a real release, test the process:

```bash
# Trigger TestPyPI publish manually
# Go to Actions → Publish to PyPI → Run workflow
# Set "Publish to TestPyPI" to true
```

Install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    enhanced-quantum-backend-selector==0.2.0
```

## Hotfix Releases

For urgent bug fixes:

1. Create hotfix branch:
   ```bash
   git checkout -b hotfix/0.2.1 v0.2.0
   ```

2. Fix the bug and add tests

3. Update version to `0.2.1` in pyproject.toml

4. Update CHANGELOG.md

5. Commit and merge to main:
   ```bash
   git commit -m "fix: critical bug in feature X"
   git checkout main
   git merge hotfix/0.2.1
   git push origin main
   ```

6. Tag and release:
   ```bash
   git tag -a v0.2.1 -m "Hotfix: critical bug in feature X"
   git push origin v0.2.1
   ```

7. Create GitHub release (triggers PyPI publish)

## Pre-releases

For beta or release candidate versions:

**Version format**: `0.2.0-beta.1`, `1.0.0-rc.1`

```bash
# Update version in pyproject.toml
version = "0.2.0-beta.1"

# Tag
git tag -a v0.2.0-beta.1 -m "Beta release v0.2.0-beta.1"
git push origin v0.2.0-beta.1

# Create GitHub release
# Check "This is a pre-release"
```

Install pre-release:

```bash
pip install enhanced-quantum-backend-selector==0.2.0b1
```

## Rollback a Release

If a release has critical issues:

1. **Yank from PyPI** (doesn't delete, but warns users):
   ```bash
   poetry publish --repository pypi --yank "Critical bug in v0.2.0"
   ```

2. **Release hotfix immediately**:
   - Follow hotfix process above
   - Increment patch version (0.2.0 → 0.2.1)

3. **Update documentation**:
   - Add warning to CHANGELOG.md
   - Document the issue and fix

## Automation

### GitHub Actions Workflows

**test.yml**: Runs on every push/PR
- Linting (ruff)
- Type checking (mypy)
- Tests (pytest)
- Coverage check (≥80%)

**docs.yml**: Runs on push to main
- Builds documentation
- Deploys to GitHub Pages

**publish.yml**: Runs on release creation
- Runs full test suite
- Builds package
- Publishes to PyPI
- Uploads artifacts

### Trusted Publishing Setup

PyPI trusted publishing is configured:

1. Go to https://pypi.org/manage/account/publishing/
2. Add publisher:
   - PyPI Project: `enhanced-quantum-backend-selector`
   - GitHub repo: `sevetseh28/enhanced_quantum_backend_selector`
   - Workflow: `publish.yml`
   - Environment: `pypi`

No API tokens needed - GitHub Actions authenticates via OIDC.

## Checklist

Before releasing:

- [ ] All tests pass locally
- [ ] Coverage ≥80%
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Documentation updated
- [ ] Examples tested
- [ ] Git tag created
- [ ] GitHub release created
- [ ] PyPI publication verified
- [ ] Installation tested

## Troubleshooting

### Publication fails

**Check GitHub Actions logs**:
- Go to Actions tab
- Click failed workflow
- Review error messages

**Common issues**:
- Version already exists on PyPI (can't overwrite)
- Test failures (fix tests first)
- Missing secrets (configure trusted publishing)

### Version conflicts

If you accidentally pushed a version that already exists:

1. Increment version (e.g., 0.2.0 → 0.2.1)
2. Update CHANGELOG.md
3. Create new tag
4. Create new release

### Documentation not deploying

**Check gh-pages branch**:

```bash
git checkout gh-pages
git log  # Verify recent commits
```

**Manually deploy**:

```bash
cd enhanced-quantum-backend-selector
poetry run mkdocs gh-deploy --force
```

## Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Poetry Versioning](https://python-poetry.org/docs/cli/#version)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
