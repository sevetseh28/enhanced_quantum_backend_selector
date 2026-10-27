# CHANGELOG


## v1.0.0 (2026-10-27)

### Bug Fixes

- **scoring**: Score by estimated success probability
  ([`44e6408`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/44e6408212b19de0f4a8d74e0d9fd87630a11ac7))

Replace the plain sum of gate and readout errors with the circuit's estimated success probability
  (product of 1 - error), computed in log space. The score is now -(1 - ESP), bounded to [-1, 0]
  even for deep circuits.

Gates without reported error on their qubits are charged the device's mean error for that gate
  instead of zero, so missing calibration data no longer makes a backend look better. Operations
  with no error data anywhere on the device are listed in the score reasons.

- **selector**: Flag incompatible backends and add seeded transpilation
  ([`f49807d`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/f49807d748d622693baf3adf152fd3995dfedd19))

Backends are now marked compatible=False with a score of -inf when the circuit needs more qubits
  than they have, when status() reports them as not operational, or when transpilation or scoring
  fails. They stay in rank_backends() results, ranked last with the reason attached, so
  require_compatible actually filters and a failing backend no longer causes an IndexError in
  select_backend().

Add a seed parameter so the same inputs produce the same ranking, break score ties by input order,
  report failures through logging instead of print, and correct docstrings that described scoring
  criteria the selector doesn't use.

- **selector**: Keep deep circuits distinguishable when ranking
  ([`bb0f061`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/bb0f06174d696cf33b69c52930a0aef5b3fff28f))

For deep circuits the estimated success probability falls below ~1e-16, 1 - ESP rounds to exactly
  1.0, and every backend scored -1.0, so the ranking silently fell back to input order.

Add CircuitScore.log_success_probability and rank by it. Transpilation runs are averaged as
  probabilities (log-mean-exp) so one run routed through a broken coupler doesn't outweigh the
  others, and the score is derived from that average so score and ranking always agree. Reasons now
  show the success probability in scientific notation.

### Documentation

- Add a diagram of how backends are scored and ranked
  ([`e9c0361`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/e9c0361622f0a3fb5f5e89cce62a443185255cd6))

- Add a short usage example at the top of the README
  ([`6ce6044`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/6ce60443ffeb5bf3c30adf669767b074f17890ca))

- Catch RuntimeError when no backend can run the circuit
  ([`269db0f`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/269db0f1e1b92125afb43f8eede1c2d058c6d5a2))

select_backend raises RuntimeError when no backend is compatible or meets min_score, but the
  examples caught ValueError and then fell back to the top of rank_backends, which is a backend that
  cannot run the circuit. Report each backend's reason instead.

- Colour the README diagram by component
  ([`d0ae2aa`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/d0ae2aa884417a2ac453db96a62fede234fe0dfa))

- Describe idle error in the scoring model and update run times
  ([`4edc9d5`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/4edc9d5928327965b362bf1600792e836844da37))

- Describe scores as success probabilities
  ([`064428d`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/064428d3617222a0ae081b81e15dc15b65b51b47))

- Describe success-probability scoring, seed and compatibility
  ([`68ecdf6`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/68ecdf6af70360bdc6047fb733c4cb8016e1b9c3))

Update the score formula and interpretation, document the seed parameter and incompatible-backend
  behaviour, fix the select_backend API reference, use live badges, and remove the caching feature
  claim, which the library doesn't implement.

- Document limitations, expected run times and log_success_probability
  ([`44b04d7`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/44b04d7fb5cea1cbf364615f9c22b91d3a11ac9b))

List what the score doesn't model (correlated errors, idle and decoherence error, queue time), how
  transpilation settings, broken couplers and missing calibration data affect it, and measured run
  times on 127-156 qubit fake IBM devices.

- Import SamplerV2 in the README usage example
  ([`dc46b1a`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/dc46b1a6c5149b8ee6b61e1b0b8fb7a5f2d7128e))

- Make the root README a symlink to the package README
  ([`70b0f2a`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/70b0f2a7f967f9c325ca7bd8d265209681838036))

The root README only linked to the package README, so visitors to the repository had to click
  through to see what the library does.

- Move QAMP checkpoint report out of the repo and credit QAMP
  ([`1186202`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/1186202ecd0ad1b14dc71df3059f19e6150416fb))

The checkpoint was a mentorship progress report rather than library documentation, and its roadmap
  is complete. Credit the program and mentor in the README instead.

- Point the docs contributing page at CONTRIBUTING.md
  ([`733b1a3`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/733b1a37ff92cab69a7a6ca80ba345a04a617a0e))

The page was a shorter copy of CONTRIBUTING.md that had already drifted from it, e.g. it installed
  pre-commit without the subdirectory config.

- Remove one-time GitHub and CI/CD setup checklists
  ([`5f02268`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/5f02268f892de4760bc88ee1bf2d902ad867bdfd))

The repository settings, secrets, environments and trusted publishing they describe are already
  configured, and they are not useful to users or contributors.

- Remove references to the removed BackendAnalyzer and its cache
  ([`29b2602`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/29b2602f5d54eab63aff2fcfa51c4feecf8b4800))

BackendAnalyzer and selector.clear_cache() were removed in 9db7eae, but the user guide, architecture
  page, API reference and contributing guide still described them.

- Use absolute links in the package README
  ([`a73baab`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/a73baabbbeaa6d97ccc1ca709dc1c04bf49b5b90))

Relative links do not resolve on PyPI. Docs pages now point to the published documentation site and
  repository files to GitHub.

### Features

- Mark the package as production/stable for 1.0
  ([`b88fc91`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/b88fc91c4e28af845f6f2f405854dcaa1d82fefc))

BREAKING CHANGE: scores now mean something different and some calls return or raise differently than
  in 0.1.0.

- CircuitScore.score is the estimated probability that the circuit runs without error, from 0 to 1,
  including gate, readout and idle error. Thresholds passed as min_score must use this scale, e.g.
  0.9 for at least a 90% success probability. - CircuitScore.score defaults to 1.0 instead of 100,
  and the new log_success_probability field is what backends are ranked by. - rank_backends returns
  incompatible backends too, last, with compatible=False and a score of 0. Filter on
  score_data.compatible if you only want usable backends. - A backend that fails to transpile or is
  not operational is reported as incompatible instead of being dropped. - BackendAnalyzer and
  BackendSelector.clear_cache were removed.

- **deps**: Support Qiskit 2.2.0 and later
  ([`6c58f19`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/6c58f193d4c7af299cadc470ef74cadeee36390c))

Lower the minimum from 2.2.3 to 2.2.0, the earliest release that is safe for the selector. Qiskit
  2.0 and 2.1 panic with PyBorrowError in high-level synthesis when backends are transpiled from
  several threads at once: about a third of parallel rankings crashed on 2.1.x and more on 2.0.x,
  while 2.2.0 completed 60 out of 60.

- **scoring**: Include idle decoherence in the success probability
  ([`3745f2f`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/3745f2fbf4bf8a1f922718aeb4a930306c522602))

Each used qubit is now charged the average infidelity of T1/T2 decay over the time it waits between
  its first and last operation, with the circuit scheduled as late as possible from the backend's
  gate durations. Explicit delays count as idle time. Missing durations and T1/T2 fall back to
  device means; backends without either get no idle error.

On ibm_kingston, ibm_fez and ibm_marrakesh, across GHZ-10, GHZ-30 and an 8-qubit QFT mirror circuit,
  the mean gap between predicted and measured success probability dropped from 0.22 to 0.14.

- **scoring**: Report the score as the estimated success probability
  ([`0b5a2ba`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/0b5a2baacd418affcdf8f7d5c49dbb6b7b377b6e))

score is now the probability that the circuit runs without error, from 0 to 1, instead of its
  negative expected error. 0.98 reads directly as a 98% chance of success and min_score=0.9 as "at
  least 90%". Incompatible backends score 0. Scores also stay distinguishable much longer on deep
  circuits: they only underflow to 0 below about 5e-324, where before they all rounded to -1.0 below
  about 1e-16.

### Refactoring

- Remove BackendAnalyzer and update scoring logic in BackendSelector and tests
  ([`9db7eae`](https://github.com/sevetseh28/enhanced_quantum_backend_selector/commit/9db7eaeeadc5bd81367cf91abace30e9c94e05f4))

### Breaking Changes

- Scores now mean something different and some calls return or raise differently than in 0.1.0.


## v0.1.0 (2026-01-20)

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
