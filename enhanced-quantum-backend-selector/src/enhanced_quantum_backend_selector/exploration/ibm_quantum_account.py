from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform", token="YOUR_IBM_QUANTUM_TOKEN", overwrite=True
)
print("Account saved successfully with ibm_quantum_platform channel!")
