


from qiskit.transpiler import Target, InstructionProperties
from qiskit.circuit.library import HGate, UGate


target = Target()

target.add_instruction(
    HGate(), # Hadamard gate
    properties={
        (0,): InstructionProperties(duration=50, error=0.001), # On Qubit 0
        (1,): InstructionProperties(duration=55, error=0.0012), # On Qubit 1
    }
)

print(target)

print(target.instructions)