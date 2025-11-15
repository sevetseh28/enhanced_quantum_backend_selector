# Automated Release Workflow

This project uses **semantic-release** to automate versioning, changelog generation, and GitHub releases based on conventional commits.

## How It Works

### 1. Conventional Commits

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Common types:**
- `feat`: New feature (triggers minor version bump, e.g., 0.1.0 → 0.2.0)
- `fix`: Bug fix (triggers patch version bump, e.g., 0.1.0 → 0.1.1)
- `docs`: Documentation changes (triggers patch version bump)
- `refactor`: Code refactoring (triggers patch version bump)
- `perf`: Performance improvements (triggers patch version bump)
- `test`: Test updates (no release)
- `chore`: Maintenance tasks (no release)
- `ci`: CI/CD changes (no release)

**Breaking changes** (trigger major version bump, e.g., 0.1.0 → 1.0.0):
```
feat!: remove deprecated API

BREAKING CHANGE: The old API has been removed
```

### 2. Automated Release Process

When you push to `main`:

1. **Tests Run**: GitHub Actions runs the full test suite
2. **Analysis**: semantic-release analyzes commits since last release
3. **Version Bump**: Determines new version based on commit types
4. **Changelog**: Auto-generates CHANGELOG.md
5. **Tag**: Creates git tag (e.g., v0.1.0)
6. **GitHub Release**: Creates release with notes
7. **PyPI Publish**: Publishes package to PyPI (if configured)

### 3. Workflow Files

**`.github/workflows/release.yml`**
- Triggers on push to `main`
- Runs semantic-release
- Creates tags and GitHub releases

**`.github/workflows/publish.yml`**
- Triggers on release publication or version tags
- Builds and publishes to PyPI

**`.releaserc.json`**
- Configuration for semantic-release
- Defines release rules and changelog format

## Release Steps

### For Developers

1. **Make changes** following conventional commits:
   ```bash
   git commit -m "feat: add new scoring algorithm"
   git commit -m "fix: correct error rate calculation"
   git commit -m "docs: update API documentation"
   ```

2. **Push to main**:
   ```bash
   git push origin main
   ```

3. **Automated release happens**:
   - Tests pass → version bumped → tag created → release published

### Manual Release (if needed)

Only use for emergencies or initial setup:

```bash
# Create tag manually
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# Or create GitHub release manually via web UI
```

## Version Determination

| Commits Since Last Release | New Version |
|-----------------------------|-------------|
| `feat: ...` | 0.1.0 → 0.2.0 |
| `fix: ...` | 0.1.0 → 0.1.1 |
| `feat!: ...` or `BREAKING CHANGE:` | 0.1.0 → 1.0.0 |
| `docs: ...` | 0.1.0 → 0.1.1 |
| `chore: ...` | No release |

## PyPI Publishing

### Setup Required

1. **Configure PyPI Trusted Publishing**:
   - Go to PyPI → Account Settings → Publishing
   - Add GitHub Actions as trusted publisher
   - Set workflow: `publish.yml`

2. **Set GitHub Secrets** (if not using trusted publishing):
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: TestPyPI token (optional)

### Testing on TestPyPI

Manually trigger publish workflow:
- Go to Actions → Publish to PyPI → Run workflow
- Select "Publish to TestPyPI"

## Benefits

✅ **No manual version management**: Versions are determined automatically
✅ **Consistent changelog**: Auto-generated from commit history
✅ **No forgotten tags**: Tags created automatically
✅ **Fast releases**: Push and go
✅ **Conventional commits**: Enforces good commit messages
✅ **Full automation**: From commit to PyPI without manual steps

## Example Workflow

```bash
# Developer workflow
git checkout -b feature/new-scoring
# ... make changes ...
git commit -m "feat: implement adaptive scoring algorithm"
git commit -m "test: add tests for adaptive scoring"
git push origin feature/new-scoring
# ... create PR, get approval, merge ...

# After merge to main (automatic):
# 1. Tests run
# 2. Version bumps to 0.2.0
# 3. Tag v0.2.0 created
# 4. GitHub release created with changelog
# 5. Package published to PyPI

# Users can now install:
pip install enhanced-quantum-backend-selector==0.2.0
```

## Troubleshooting

**No release created?**
- Check commit messages follow conventional commits
- Only `feat`, `fix`, `docs`, `refactor`, `perf` trigger releases
- Check GitHub Actions logs

**Version incorrect?**
- Verify commit types
- Check for BREAKING CHANGE in commit body

**PyPI publish failed?**
- Verify trusted publishing is configured
- Check PyPI credentials in GitHub secrets
- Ensure package name is available on PyPI
