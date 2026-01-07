---
**Title:** CI Failing: Missing qiskit-aer dependency and semantic-release npm configuration in Automated Release

**Body:**
The CI workflow for the Automated Release job failed due to two issues:

1. **Python Dependency Error:**
   - tests/test_backend_selector.py imports AerSimulator from qiskit_aer, but qiskit-aer is not installed in the CI environment.
   - Solution: Add qiskit-aer to Poetry dependencies with poetry add qiskit-aer --dev.

2. **Semantic Release Error:**
   - The semantic-release npm plugin is configured, but the repository does not have a package.json.
   - Solution: Remove the @semantic-release/npm plugin from workflow/configuration if this is a Python-only repo.

**Job Reference:**
https://github.com/sevetseh28/enhanced_quantum_backend_selector/actions/runs/20766433295/job/59633468993

---