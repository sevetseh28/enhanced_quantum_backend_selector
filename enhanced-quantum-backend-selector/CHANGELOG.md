# CHANGELOG


## v0.1.0 (2026-01-20)


## v0.0.0 (2026-01-20)

### Bug Fixes

- Add author information in pyproject.toml
  ([`74f01a4`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/74f01a4c35c46b36639962bf30a4528191a5c1fc))

- Add explicit permissions to workflow jobs for security
  ([`2f03ba0`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/2f03ba06511c9cd627a86ab7edd8e90ac47b20ee))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Add explicit pull_request event types to trigger test workflow on PR updates
  ([`595dd85`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/595dd853084bd7498565b41b00099398dc2d7972))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Add qiskit-aer dependency and disable npm publishing in semantic-release
  ([`5660fd8`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/5660fd89d905c73e6cca47a52efb1e1cea84712c))

- Add qiskit-aer and qiskit-ibm-runtime to Poetry dev dependencies - Update poetry.lock with new
  dependencies - Configure @semantic-release/npm with npmPublish: false to prevent package.json
  requirement - Add publishCmd to @semantic-release/exec to build Python packages

Fixes CI failure caused by missing qiskit_aer module and semantic-release npm configuration error

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Add trailing slash to out-file-path in publish workflow
  ([`bcdd1cf`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/bcdd1cf2f06b37c062f8ad65f88bffb7695571d2))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Configure commit tags to match original semantic-release behavior
  ([`039c2a8`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/039c2a84b02a8f2ca5ed9f9fe34d22a2059cca6d))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Correct backend selection reference in chemistry circuits example
  ([`3086518`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/308651898e06452a8e039544d6fcb47cef20c626))

- Correct conditional logic for TestPyPI and PyPI publish steps
  ([`3aaa1ec`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/3aaa1eca6f56a69845b21abe38158e68dd35759a))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Correct workflow job dependencies and eliminate redundant builds
  ([`a755f30`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/a755f307165bfeafc87a82b944b1fc0e130ee360))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Enhance devcontainer setup with detailed post-create commands and remove readme reference from
  pyproject.toml
  ([`31eda9e`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/31eda9e95668ce3b47894ea826a7a16eef5713a2))

- Refine PyPI publish condition to properly respect test-pypi input
  ([`ac6cb77`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/ac6cb7797a3d38faa344a8f0bcbff15f2ed8a1bb))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Remove permissions from reusable workflow to allow caller control
  ([`59167ef`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/59167ef34a58dbafff6c3f511fa95a1c0899bb09))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Reorganize semantic_release config to match official documentation structure
  ([`9a6428d`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/9a6428dc7ff19e4dac6b74ffe644a521ce48871d))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Restore push.tags trigger and use reliable build approach for publish workflow
  ([`6db66e6`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/6db66e670b51aea7787fc1dad9adb8aa39d356ac))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Update class docstring for clarity on scoring criteria
  ([`fe82071`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/fe820717d61fd9d93b688e955ec572813da11663))

- Use correct format for out-file-path (no trailing slash)
  ([`a347b08`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/a347b08be25ed35dbbe3ce8c1bd3e9258452076a))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Use root_options for dry-run and update deprecated config
  ([`0698c1f`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/0698c1fcf885681fb806898f4b5ad39746b47408))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Use transpiled circuit and consider error rates for scoring only + CI/CD fixes and docs
  ([`6924391`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/69243914113434474458d7d5376ce30ff997e184))

fix: use transpiled circuit and consider error rates for scoring only + CI/CD fixes and docs

- **ci**: Remove twine check and IMPLEMENTATION_SUMMARY.md
  ([`cbb1ff0`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/cbb1ff06c3886c77a62db12953961c1e79dbc42b))

- Remove IMPLEMENTATION_SUMMARY.md as requested - Remove twine check from publish workflow (not
  needed, pypa action validates) - Update RELEASE.md documentation to reflect workflow changes

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- **ci/cd**: Add python-semantic-release to development dependencies and use devcontainer on CI/CD
  job ([#14](https://github.com/sevetseh28/enhanced_quantum_backend_selector/pull/14),
  [`9948fb5`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/9948fb5768e3a14f48862225bca206069e196984))

- **ci/cd**: Install dev deps in release workflow
  ([`f6ab0aa`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/f6ab0aaa13dd2efa40e33143eddcc80447d798b9))

- **docs**: Improve security guidance for API token handling
  ([`0b0bcf6`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/0b0bcf6347370336b83a41f4f91aec5d4f37f331))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

### Documentation

- Add CI/CD verification checklist for maintainers
  ([`ba15121`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/ba151213e41cc38a5f2776fd187ca54eb9ab37cd))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Add implementation summary for PR review
  ([`33e653e`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/33e653e33580ae2dc716e0270657b3602828df0a))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Enhance root README and update CHANGELOG
  ([`e0b6ec3`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/e0b6ec39c18d92cab5dda939154ccd7d67a56851))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Update all documentation to reference python-semantic-release
  ([`695790f`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/695790f09d941b8f0f9dcab508b217b8e25dcd4a))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Update RELEASE.md to reference python-semantic-release
  ([`1de4f94`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/1de4f94a64fd2377fc7bc6e3ce41b1fa39cc9914))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

### Features

- Add configurable transpilation runs for improved scoring accuracy
  ([`7a89010`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/7a89010925d3d1ef60355518185827d845d56e5d))

- Add dry-run release test workflow with reusable workflow pattern
  ([`3275acc`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/3275acc9011d3ccbae1a1b4b80003a6acb93827e))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Add fractional gates analysis
  ([`32d916f`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/32d916f82aaded86884e81468a234b052a83d9ae))

- Complete implementation of Enhanced Quantum Backend Selector v0.1.0
  ([`a9c7966`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/a9c796687a5fb16b35ec4dbe60bccc6650c641a4))

- Implement intelligent backend selection with multi-criteria scoring - Add comprehensive testing
  suite (23 tests, 93.79% coverage) - Include canonical quantum circuit validation - Add CI/CD
  workflows for GitHub Actions - Configure pre-commit hooks for code quality - Add documentation
  with MkDocs - Include usage examples (basic and advanced) - Prepare for PyPI publishing

- Enhance backend scoring by adding support for fractional gates and improving transpilation
  optimization
  ([`72554bc`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/72554bca331379680035a8f69d12f9031494ab1d))

- Enhance backend scoring by averaging multiple transpilation runs and update tests for new scoring
  logic
  ([`b557cf7`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/b557cf75b74ff8153504c41255a11b8aa340a4c8))

- Enhance error calculation by modularizing single, two-qubit, and readout error summation
  ([`1d1d5f5`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/1d1d5f526ca8193c295df51ffc1a56095ac9c374))

- Migrate from Node semantic-release to python-semantic-release
  ([`224c78d`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/224c78de4a1085cc3aacb691824023be7e31f100))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- **ci**: Finalize CI/CD configuration with comprehensive documentation
  ([`821b75b`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/821b75bfdf3201528ce9443e386191e0515f68c3))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

### Refactoring

- Centralize SKIP_OPERATIONS constant for improved maintainability and clarity
  ([`c09a237`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/c09a23780ecb0e1e5f0f50a601fc9e6f7baa7410))

- Clarify comments on fractional gates detection and usage in backend scoring
  ([`774d81c`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/774d81c89ffc5799b814b7b14bda0eed93cdec87))

- Consolidate release workflows and remove reusable configuration
  ([`d4bb1ae`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/d4bb1ae926598d2ba8989d8fbdee46149c4f3668))

- Improve scoring logic and add unit tests for CircuitScorer (manual)
  ([`78a2407`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/78a2407e093554dbc089febccf10d09f812f8a95))

- Move readme to root and also github workflows
  ([`03283da`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/03283da838b6ddd6d093edac5f8905c01af2de1e))

- Remove redundant branch configuration from pyproject.toml
  ([`8b8a550`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/8b8a5509f4bbe47cf351f0d9e6356c6cf591c9b8))

Co-authored-by: sevetseh28 <13895313+sevetseh28@users.noreply.github.com>

- Replace hardcoded skip operations with a constant set for improved maintainability
  ([`7f6b817`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/7f6b81733222713a6fe4ee74f77512139fea35b1))

- Set default transpilation_runs to 3 in BackendSelector
  ([`054e85a`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/054e85a6d39401f62fe739ba30f246aa8d9317ba))

- Simplify fractional gates detection in backend scoring
  ([`d35adaf`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/d35adaf999e984c3dd2c6831c5675cbf6955f234))

- Streamline metric printing in basic usage example
  ([`c773334`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/c77333495f97b1fe90862034379f6fc481021fd2))
