from typing import Callable

from braket.circuits import Circuit  # noqa
from qiskit import QuantumCircuit  # noqa

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage

PreProcessor = Callable[[str], any]


class PreProcessingManager:

    def __init__(self):
        self._pre_processing_methods: dict[AssemblerLanguage, PreProcessor] = {}
        self._language_nodes = dict()

    def register(self, language: AssemblerLanguage):
        def decorator(transpile_method: PreProcessor):
            self._pre_processing_methods[language] = transpile_method
            return transpile_method

        return decorator

    def get_preprocessor(self, language: AssemblerLanguage) -> PreProcessor:
        preprocessor = self._pre_processing_methods.get(language)
        if preprocessor is None:
            preprocessor = lambda circuit: circuit
        return preprocessor


preprocessing_manager = PreProcessingManager()


@preprocessing_manager.register(AssemblerLanguage.QISKIT)
def pre_process_qiskit(program: str) -> QuantumCircuit:
    """
    since the qiskit circuit modifies the circuit object instead of simple returning the object (it
    returns the instruction set) the 'qiskit_circuit' is modified from the exec
    """
    circuit_globals = {"QuantumCircuit": QuantumCircuit}
    exec(program, circuit_globals)
    return circuit_globals["qiskit_circuit"]


@preprocessing_manager.register(AssemblerLanguage.BRAKET)
def pre_process_braket(program: str) -> Circuit:
    """
        braket.Circuit needs to be included here as an import here so eval works with the type
    """
    circuit_globals = {"Circuit": Circuit}
    circuit: Circuit = eval(program, circuit_globals)
    return circuit
