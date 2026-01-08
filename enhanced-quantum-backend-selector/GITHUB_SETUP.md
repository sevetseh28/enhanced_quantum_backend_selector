# GitHub Configuration Guide

This document provides step-by-step instructions for configuring GitHub repository settings, secrets, and environments required for the CI/CD pipeline.

## Table of Contents

1. [Repository Settings](#repository-settings)
2. [GitHub Secrets](#github-secrets)
3. [GitHub Environments](#github-environments)
4. [PyPI Trusted Publishing](#pypi-trusted-publishing)
5. [Branch Protection Rules](#branch-protection-rules)
6. [Verification](#verification)

## Repository Settings

### General Settings

Navigate to **Settings** → **General**:

- **Default branch**: `main` ✓
- **Allow merge commits**: Enabled (recommended)
- **Allow squash merging**: Enabled (recommended)
- **Allow rebase merging**: Optional
- **Automatically delete head branches**: Enabled (recommended)

### GitHub Pages

Navigate to **Settings** → **Pages**:

- **Source**: Deploy from a branch
- **Branch**: `gh-pages` / `/ (root)`
- **Build and deployment**: GitHub Actions (automatically configured by docs workflow)

URL: https://sevetseh28.github.io/enhanced_quantum_backend_selector

## GitHub Secrets

### Overview

Secrets are encrypted environment variables used in workflows. Configure in **Settings** → **Secrets and variables** → **Actions**.

### Required Secrets

#### `CODECOV_TOKEN` (Optional but Recommended)

**Purpose**: Upload test coverage reports to Codecov

**How to get**:
1. Go to https://codecov.io/
2. Log in with GitHub
3. Add your repository
4. Navigate to **Settings** → **General** → **Repository Upload Token**
5. Copy the token

**How to add**:
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `CODECOV_TOKEN`
4. Value: Paste the token from Codecov
5. Click **Add secret**

**Note**: Coverage reporting will still work without this token, but may have limitations.

### Legacy Secrets (Not Needed with Trusted Publishing)

These are **not required** if using PyPI Trusted Publishing (recommended approach):

#### `PYPI_API_TOKEN` (Legacy)

**Purpose**: Publish to PyPI (alternative to Trusted Publishing)

**How to get**:
1. Go to https://pypi.org/
2. Log in
3. Go to **Account settings** → **API tokens**
4. Click **Add API token**
5. Token name: `enhanced-quantum-backend-selector-ci`
6. Scope: Select specific project (if it exists) or "Entire account"
7. Generate token
8. **Copy immediately** (shown only once!)

**How to add**: Same as CODECOV_TOKEN above, name it `PYPI_API_TOKEN`

#### `TEST_PYPI_API_TOKEN` (Legacy)

Same as above but for https://test.pypi.org/

## GitHub Environments

Environments provide deployment protection and secrets scoped to specific workflows.

### Create Environments

Navigate to **Settings** → **Environments**

### `pypi` Environment (Production)

1. Click **New environment**
2. Name: `pypi`
3. Click **Configure environment**

**Environment Protection Rules** (Recommended):
- ✅ **Required reviewers**: Add maintainers who must approve PyPI deployments
  - This adds a manual approval step before publishing to production PyPI
  - Recommended for production safety
- ⏱️ **Wait timer**: Optional (e.g., 5 minutes) to allow cancellation of accidental deployments
- 🏷️ **Deployment branches**: Only `main` branch and tags matching `v*.*.*`

**Environment Secrets**:
- None needed when using Trusted Publishing ✓
- If using legacy tokens, add `PYPI_API_TOKEN` here instead of repository secrets

**Trusted Publishing**:
- Configured on PyPI side (see [PyPI Trusted Publishing](#pypi-trusted-publishing))

### `testpypi` Environment (Testing)

1. Click **New environment**
2. Name: `testpypi`
3. Click **Configure environment**

**Environment Protection Rules**:
- No protection needed (safe for testing)
- **Deployment branches**: Any branch (allows testing from feature branches)

**Environment Secrets**:
- None needed when using Trusted Publishing ✓
- If using legacy tokens, add `TEST_PYPI_API_TOKEN` here

**Trusted Publishing**:
- Configured on TestPyPI side (see [PyPI Trusted Publishing](#pypi-trusted-publishing))

### Environment Variables

If needed, you can also add non-secret environment-specific variables here.

## PyPI Trusted Publishing

**Trusted Publishing** is the recommended, most secure method for publishing to PyPI. It uses OpenID Connect (OIDC) for authentication, eliminating the need for long-lived API tokens.

### Advantages

- ✅ No API tokens to manage or rotate
- ✅ Automatic, per-workflow authentication
- ✅ Reduced risk of token leakage
- ✅ Cryptographically signed, tamper-proof
- ✅ Auditable publish history

### Setup on PyPI (Production)

#### For Existing Projects

1. Go to https://pypi.org/ and log in
2. Navigate to your project: https://pypi.org/manage/project/enhanced-quantum-backend-selector/
3. Go to **Publishing** tab
4. Scroll to **Trusted Publishers**
5. Click **Add a new publisher**
6. Fill in the form:
   ```
   PyPI Project Name:    enhanced-quantum-backend-selector
   Owner:                sevetseh28
   Repository name:      enhanced_quantum_backend_selector
   Workflow name:        publish.yml
   Environment name:     pypi
   ```
7. Click **Add**

#### For New Projects (First Publish)

For projects not yet published to PyPI:

**Option 1: Pending Publisher (Recommended)**

1. Go to https://pypi.org/manage/account/publishing/
2. Click **Add a new pending publisher**
3. Fill in the same form as above
4. Click **Add**
5. The publisher will be activated on first successful publish

**Option 2: Manual First Publish** (only if pending publisher is not available)

1. Generate a scoped API token on PyPI
2. Configure credentials securely (never in command line):
   ```bash
   # Method 1: Using .pypirc (recommended)
   cat > ~/.pypirc << EOF
   [pypi]
   username = __token__
   password = pypi-YOUR-API-TOKEN
   EOF
   chmod 600 ~/.pypirc
   
   # Method 2: Using environment variable
   export POETRY_PYPI_TOKEN_PYPI=pypi-YOUR-API-TOKEN
   ```
3. Do the first publish:
   ```bash
   poetry build
   poetry publish  # Uses credentials from .pypirc or env var
   ```
4. Then configure Trusted Publishing as in "For Existing Projects" above
5. Delete the API token from PyPI and remove from `~/.pypirc`

### Setup on TestPyPI (Testing)

Same process as PyPI but on https://test.pypi.org/:

1. Go to https://test.pypi.org/manage/account/publishing/
2. Click **Add a new pending publisher**
3. Fill in:
   ```
   PyPI Project Name:    enhanced-quantum-backend-selector
   Owner:                sevetseh28
   Repository name:      enhanced_quantum_backend_selector
   Workflow name:        publish.yml
   Environment name:     testpypi
   ```
4. Click **Add**

### Verification

After configuring Trusted Publishing:

1. **Check PyPI dashboard**: Trusted publishers should appear in the Publishing tab
2. **Test with TestPyPI**:
   - Go to **Actions** → **Publish to PyPI**
   - Click **Run workflow**
   - Select `main` branch
   - Set "Publish to TestPyPI instead of PyPI" to **true**
   - Click **Run workflow**
   - Monitor the workflow run
3. **Verify on TestPyPI**: Check https://test.pypi.org/project/enhanced-quantum-backend-selector/

### Workflow Configuration

The workflows are already configured for Trusted Publishing. Key settings in `publish.yml`:

```yaml
permissions:
  id-token: write  # Required for OIDC authentication
  contents: read

environment: 
  name: ${{ github.event.inputs.test-pypi == 'true' && 'testpypi' || 'pypi' }}
```

The `pypa/gh-action-pypi-publish@release/v1` action automatically uses Trusted Publishing when `id-token: write` permission is present.

## Branch Protection Rules

Protect the `main` branch to ensure quality and prevent accidental changes.

Navigate to **Settings** → **Branches** → **Add rule**

### Configuration

**Branch name pattern**: `main`

**Protect matching branches**:

- ✅ **Require a pull request before merging**
  - ✅ Required approvals: 1 (or more for critical projects)
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ⬜ Require review from Code Owners (optional, requires CODEOWNERS file)

- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Required status checks:
    - `test` (from test.yml workflow)
    - `build` (from test.yml workflow)
    - `build-docs` (optional, from docs.yml workflow)

- ✅ **Require conversation resolution before merging**

- ✅ **Require signed commits** (optional but recommended)

- ✅ **Include administrators** (recommended - even admins must follow rules)

- ✅ **Restrict who can push to matching branches** (optional)
  - Restrict pushes that create matching branches (recommended)

- ✅ **Allow force pushes**: ❌ Disabled (recommended)

- ✅ **Allow deletions**: ❌ Disabled (recommended)

**Save changes**

### Tag Protection

To protect release tags from deletion:

Navigate to **Settings** → **Tags** → **New rule**

- **Tag name pattern**: `v*.*.*`
- ✅ **Prevent tag deletions**
- **Add rule**

This prevents accidental deletion of version tags.

## Verification

### Checklist

After completing configuration, verify:

#### Secrets
- [ ] `CODECOV_TOKEN` added (if using Codecov)
- [ ] Other secrets added as needed

#### Environments
- [ ] `pypi` environment created with appropriate protection
- [ ] `testpypi` environment created
- [ ] Environment deployment branches configured

#### Trusted Publishing
- [ ] PyPI trusted publisher configured
- [ ] TestPyPI trusted publisher configured
- [ ] Test publish to TestPyPI successful

#### Branch Protection
- [ ] `main` branch protection enabled
- [ ] Required status checks configured
- [ ] Pull request reviews required

#### Workflows
- [ ] Test workflow runs successfully on PR
- [ ] Documentation builds successfully
- [ ] Can manually trigger publish workflow

### Test the Complete Pipeline

1. **Create a test branch**:
   ```bash
   git checkout -b test/ci-verification
   echo "# Test" >> TEST.md
   git add TEST.md
   git commit -m "test(ci): verify CI/CD configuration"
   git push origin test/ci-verification
   ```

2. **Create a Pull Request** and verify:
   - ✅ Test workflow runs
   - ✅ Build job completes
   - ✅ Coverage is uploaded (if Codecov configured)
   - ✅ Documentation builds

3. **Test Manual Publish** (to TestPyPI):
   - Go to **Actions** → **Publish to PyPI**
   - Run workflow with TestPyPI option
   - Verify successful publish
   - Check https://test.pypi.org/project/enhanced-quantum-backend-selector/

4. **Merge to main** (from a test branch with a proper conventional commit):
   - ✅ Release workflow runs
   - ✅ Version is bumped (if commit type triggers release)
   - ✅ CHANGELOG is updated
   - ✅ GitHub Release is created
   - ✅ Publish workflow runs automatically
   - ✅ Package appears on PyPI

## Troubleshooting

### Workflow Failures

**Test workflow fails**:
- Check **Actions** tab for detailed logs
- Verify Python version compatibility
- Ensure all dependencies in `pyproject.toml` are resolvable

**Release workflow fails**:
- Verify conventional commit format
- Check python-semantic-release configuration in `pyproject.toml`
- Ensure python-semantic-release GitHub Action is properly configured (check workflow file)

**Publish workflow fails**:
- Verify Trusted Publishing is configured correctly
- Check environment name matches in workflow and PyPI
- Ensure `id-token: write` permission is set
- Review workflow logs for specific error

### Trusted Publishing Issues

**"Trusted publishing authentication not configured"**:
- Verify publisher is added on PyPI/TestPyPI
- Check repository, workflow name, environment name match exactly
- For new projects, use pending publisher feature

**Permission denied**:
- Verify `id-token: write` in workflow permissions
- Check environment exists in repository settings
- Ensure workflow name is exact: `publish.yml` (not `Publish to PyPI`)

### Secrets Not Working

**Secret not accessible in workflow**:
- Verify secret name matches exactly (case-sensitive)
- Check secret is added to correct scope (repository vs environment)
- For environment secrets, verify workflow references environment

**Token expired or invalid**:
- Regenerate token on PyPI/Codecov
- Update secret in GitHub
- For PyPI, consider switching to Trusted Publishing

## Maintenance

### Regular Tasks

- **Review access**: Periodically review who has admin access
- **Update tokens**: Rotate API tokens if used (or switch to Trusted Publishing)
- **Monitor workflows**: Check for deprecated actions or features
- **Test pipeline**: Occasionally test full pipeline end-to-end

### Updates

- **GitHub Actions**: Dependabot can auto-update action versions
- **Secrets rotation**: Set calendar reminders if using tokens
- **Configuration review**: Review this guide annually

## Additional Resources

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)

## Support

If you encounter issues:
1. Check this guide
2. Review workflow logs in Actions tab
3. Consult [RELEASE.md](RELEASE.md)
4. Open an issue on GitHub
5. Contact repository maintainers

---

**Last Updated**: December 2025
**Maintained By**: @sevetseh28
