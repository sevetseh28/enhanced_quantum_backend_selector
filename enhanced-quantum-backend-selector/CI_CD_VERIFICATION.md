# CI/CD Setup Verification Checklist

This checklist helps verify that the CI/CD pipeline is properly configured and functioning.

## Pre-Deployment Checklist

Use this checklist before the first production release:

### 1. GitHub Repository Configuration

- [ ] **Branch Protection** ([GITHUB_SETUP.md](GITHUB_SETUP.md#branch-protection-rules))
  - [ ] `main` branch protection enabled
  - [ ] Require pull request reviews (minimum 1 approval)
  - [ ] Require status checks: `test`, `build`
  - [ ] Require conversation resolution
  - [ ] Include administrators in restrictions

- [ ] **Tag Protection**
  - [ ] Pattern `v*.*.*` protected from deletion

- [ ] **GitHub Pages**
  - [ ] Enabled and configured for documentation
  - [ ] URL: https://sevetseh28.github.io/enhanced_quantum_backend_selector

### 2. GitHub Secrets

- [ ] **Codecov** ([GITHUB_SETUP.md](GITHUB_SETUP.md#codecov_token-optional-but-recommended))
  - [ ] `CODECOV_TOKEN` added (optional but recommended)
  - [ ] Test by creating a PR and checking coverage upload

### 3. GitHub Environments

- [ ] **pypi Environment** ([GITHUB_SETUP.md](GITHUB_SETUP.md#pypi-environment-production))
  - [ ] Environment created
  - [ ] Deployment protection configured (reviewers recommended)
  - [ ] Deployment branches: `main` and tags matching `v*.*.*`

- [ ] **testpypi Environment** ([GITHUB_SETUP.md](GITHUB_SETUP.md#testpypi-environment-testing))
  - [ ] Environment created
  - [ ] Deployment branches: Any branch (for testing)

### 4. PyPI Trusted Publishing

- [ ] **PyPI Production** ([GITHUB_SETUP.md](GITHUB_SETUP.md#setup-on-pypi-production))
  - [ ] Pending publisher added on https://pypi.org/manage/account/publishing/
  - [ ] Configuration:
    - Project: `enhanced-quantum-backend-selector`
    - Owner: `sevetseh28`
    - Repository: `enhanced_quantum_backend_selector`
    - Workflow: `publish.yml`
    - Environment: `pypi`

- [ ] **TestPyPI** ([GITHUB_SETUP.md](GITHUB_SETUP.md#setup-on-testpypi-testing))
  - [ ] Pending publisher added on https://test.pypi.org/manage/account/publishing/
  - [ ] Same configuration as above, environment: `testpypi`

### 5. Workflow Files Validation

- [ ] **test.yml**
  - [ ] YAML syntax valid
  - [ ] Triggers on push/PR to `main` and `develop`
  - [ ] Python 3.12 and 3.13 matrix
  - [ ] All Poetry commands correct

- [ ] **release.yml**
  - [ ] YAML syntax valid
  - [ ] Triggers on push to `main`
  - [ ] `@semantic-release/exec@6` installed
  - [ ] Poetry version command configured in `.releaserc.json`

- [ ] **publish.yml**
  - [ ] YAML syntax valid
  - [ ] `id-token: write` permission set
  - [ ] Environments configured correctly
  - [ ] Trusted Publishing action used

- [ ] **docs.yml**
  - [ ] YAML syntax valid
  - [ ] MkDocs build and deploy configured

### 6. Configuration Files

- [ ] **.releaserc.json**
  - [ ] JSON syntax valid
  - [ ] All plugins listed: commit-analyzer, release-notes-generator, changelog, exec, git, github
  - [ ] `prepareCmd` runs `poetry version ${nextRelease.version}`
  - [ ] Assets include CHANGELOG.md and pyproject.toml

- [ ] **pyproject.toml**
  - [ ] Version field present (will be managed by semantic-release)
  - [ ] Poetry configuration complete
  - [ ] All dependencies listed

## Testing Checklist

Verify the pipeline works before first production release:

### 1. Test Workflow (PR)

- [ ] Create test branch:
  ```bash
  git checkout -b test/ci-verification
  echo "# CI Test" >> CI_TEST.md
  git add CI_TEST.md
  git commit -m "test(ci): verify CI/CD pipeline"
  git push origin test/ci-verification
  ```

- [ ] Create Pull Request
- [ ] Verify workflows run:
  - [ ] Test workflow completes successfully
  - [ ] Build job creates artifacts
  - [ ] Coverage uploaded to Codecov (if configured)
  - [ ] Documentation builds

- [ ] Verify branch protection:
  - [ ] Cannot merge without approval (if configured)
  - [ ] Cannot merge with failing checks

### 2. Test Manual Publish (TestPyPI)

- [ ] Navigate to **Actions** → **Publish to PyPI**
- [ ] Click **Run workflow**
- [ ] Select branch: `main` or test branch
- [ ] Set "Publish to TestPyPI instead of PyPI": **true**
- [ ] Click **Run workflow**
- [ ] Verify:
  - [ ] Workflow completes successfully
  - [ ] Package appears on https://test.pypi.org/project/enhanced-quantum-backend-selector/
  - [ ] Can install: `pip install -i https://test.pypi.org/simple/ enhanced-quantum-backend-selector`

### 3. Test Release Process (Dry Run)

**Option A: Local Dry Run** (recommended first)

- [ ] Install semantic-release dependencies:
  ```bash
  npm install -g \
    semantic-release@23 \
    @semantic-release/changelog@6 \
    @semantic-release/exec@6 \
    @semantic-release/git@10 \
    @semantic-release/github@10 \
    conventional-changelog-conventionalcommits@7
  ```

- [ ] Run dry-run:
  ```bash
  cd /path/to/enhanced_quantum_backend_selector
  npx semantic-release --dry-run
  ```

- [ ] Verify dry-run output:
  - [ ] Analyzes commits correctly
  - [ ] Determines correct version bump
  - [ ] Shows what would be released

**Option B: Test Release Branch** (if confident)

- [ ] Create feature branch with conventional commit:
  ```bash
  git checkout -b feat/test-release
  echo "# Feature test" >> FEATURE_TEST.md
  git add FEATURE_TEST.md
  git commit -m "feat(test): test automatic release process"
  git push origin feat/test-release
  ```

- [ ] Create and merge PR to `main`
- [ ] Monitor **Actions** → **Automated Release**
- [ ] Verify:
  - [ ] Release workflow runs
  - [ ] Version bumped in pyproject.toml
  - [ ] CHANGELOG.md updated
  - [ ] Git tag created (e.g., `v0.2.0`)
  - [ ] GitHub Release created
  - [ ] Build artifacts attached

### 4. Test Automatic Publish (After Release)

- [ ] After release is created, monitor **Actions** → **Publish to PyPI**
- [ ] Verify:
  - [ ] Publish workflow triggers automatically
  - [ ] Tests run successfully
  - [ ] Package builds
  - [ ] Publishes to PyPI (production)
  - [ ] Package appears on https://pypi.org/project/enhanced-quantum-backend-selector/

- [ ] Test installation from PyPI:
  ```bash
  pip install enhanced-quantum-backend-selector
  python -c "from enhanced_quantum_backend_selector import BackendSelector; print('Success!')"
  ```

## Post-Deployment Verification

After first production release:

### 1. Verify Release

- [ ] **GitHub Release**
  - [ ] Release visible at https://github.com/sevetseh28/enhanced_quantum_backend_selector/releases
  - [ ] Release notes generated correctly
  - [ ] Build artifacts (`.whl` and `.tar.gz`) attached

- [ ] **Git Tags**
  - [ ] Tag created: `git tag -l`
  - [ ] Tag pushed to remote

- [ ] **Version Updates**
  - [ ] `pyproject.toml` version updated
  - [ ] CHANGELOG.md updated with release
  - [ ] Version commit created by semantic-release

### 2. Verify PyPI Package

- [ ] **PyPI Page**
  - [ ] Package visible at https://pypi.org/project/enhanced-quantum-backend-selector/
  - [ ] Correct version displayed
  - [ ] Description renders correctly
  - [ ] Links work (homepage, docs, issues, etc.)
  - [ ] Classifiers correct

- [ ] **Installation**
  - [ ] Can install: `pip install enhanced-quantum-backend-selector`
  - [ ] Correct version installed: `pip show enhanced-quantum-backend-selector`
  - [ ] Package imports successfully

- [ ] **Files**
  - [ ] Download files section shows `.whl` and `.tar.gz`
  - [ ] File sizes reasonable
  - [ ] Hashes present

### 3. Verify Documentation

- [ ] **GitHub Pages**
  - [ ] Accessible at https://sevetseh28.github.io/enhanced_quantum_backend_selector/
  - [ ] Up to date with latest changes
  - [ ] Navigation works
  - [ ] API reference complete

### 4. Verify Workflows

- [ ] All workflow runs successful in **Actions** tab
- [ ] No failed jobs
- [ ] Artifacts retained correctly
- [ ] Logs clean (no unexpected errors)

## Ongoing Monitoring

After initial setup, monitor regularly:

### Weekly

- [ ] Check **Actions** tab for any failed workflows
- [ ] Review **Security** tab for alerts
- [ ] Check **Dependabot** for dependency updates

### Monthly

- [ ] Verify Codecov integration working (if used)
- [ ] Review PyPI download statistics
- [ ] Update dependencies if needed

### Quarterly

- [ ] Review and update documentation
- [ ] Test complete release process end-to-end
- [ ] Review GitHub environment protection rules
- [ ] Audit GitHub secrets and permissions

## Troubleshooting

If issues arise, consult:

1. **[RELEASE.md](RELEASE.md)** - Release process and troubleshooting
2. **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - Configuration troubleshooting
3. **Workflow logs** - GitHub Actions tab → Select workflow → View logs
4. **GitHub Issues** - Open issue if problem persists

## Common Issues and Solutions

### Release not created on merge to main

**Check**:
- [ ] Commits use conventional format (`feat:`, `fix:`, etc.)
- [ ] Commit types trigger releases (not `chore`, `test`, `ci`)
- [ ] Release workflow didn't fail (check Actions)

### PyPI publish fails

**Check**:
- [ ] Trusted Publishing configured correctly on PyPI
- [ ] Environment name matches in workflow and PyPI setup
- [ ] `id-token: write` permission in workflow
- [ ] Tests passing in publish workflow

### Version conflict

**Check**:
- [ ] Version in `pyproject.toml` not manually edited
- [ ] Git tags not manually created or deleted
- [ ] Semantic-release has write access

## Completion Sign-off

When all items checked:

- **Verified by**: ___________________
- **Date**: ___________________
- **First Release Version**: ___________________
- **PyPI URL**: https://pypi.org/project/enhanced-quantum-backend-selector/
- **Notes**: ___________________

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**Maintained by**: @sevetseh28
