from typing import Callable

from braket.circuits import Circuit  # noqa
from pyquil import Program
from qiskit import QuantumCircuit  # noqa
from qrisp import QuantumCircuit as QrispQC

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage

PreProcessor = Callable[[str], any]

"""This Class handles all preprocessing that is needed to transform a circuit string into a circuit object"""


class PreProcessingManager:
    def __init__(self):
        self._preprocessing_methods: dict[AssemblerLanguage, PreProcessor] = {}
        self._language_nodes = dict()

    def register(self, language: AssemblerLanguage):
        def decorator(transpile_method: PreProcessor):
            self._preprocessing_methods[language] = transpile_method
            return transpile_method

        return decorator

    def get_preprocessor(self, language: AssemblerLanguage) -> PreProcessor:
        """Either returns the registered preprocessing method or a method that returns the input"""

        preprocessor = self._preprocessing_methods.get(language)

        def return_input(circuit: any) -> any:
            return circuit

        if preprocessor is None:
            preprocessor = return_input

        return preprocessor


preprocessing_manager = PreProcessingManager()


@preprocessing_manager.register(AssemblerLanguage.QISKIT)
def preprocess_qiskit(program: str) -> QuantumCircuit:
    """
    since the qiskit circuit modifies the circuit object instead of simple returning the object
    (it returns the QiskitCircuit from the instruction set) the 'qiskit_circuit' is modified from the exec
    """
    circuit_globals = {"QuantumCircuit": QuantumCircuit}
    exec(program, circuit_globals)
    return circuit_globals["qiskit_circuit"]


@preprocessing_manager.register(AssemblerLanguage.BRAKET)
def preprocess_braket(program: str) -> Circuit:
    """braket.Circuit needs to be included here as an import here so eval works with the type"""
    circuit_globals = {"Circuit": Circuit}
    return eval(program, circuit_globals)


@preprocessing_manager.register(AssemblerLanguage.QRISP)
def preprocess_qrisp(program: str) -> QrispQC:
    """qrisp.QuantumCircuit needs to be included here as an import so eval works with the type"""
    circuit_globals = {"QuantumCircuit": QrispQC}
    exec(program, circuit_globals)
    return circuit_globals["circuit"]


@preprocessing_manager.register(AssemblerLanguage.QUIL)
def preprocess_quil(program: str) -> Program:
    """quil.QuantumCircuit needs to be included here as an import so eval works with the type"""
    exec(program, globals())
    return globals().get("program")
