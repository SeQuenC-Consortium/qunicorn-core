import dataclasses
from functools import reduce
from typing import Callable, Union

import qiskit.circuit
import qrisp.circuit
from braket.circuits import Circuit
from braket.circuits.serialization import IRType
from pydantic.fields import defaultdict
from rustworkx import PyDiGraph, dijkstra_shortest_paths
from braket.ir.openqasm import Program as OpenQASMProgram
import qiskit.qasm2
import qiskit.qasm3

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage


@dataclasses.dataclass
class TranspileStrategyStep:
    src_language: AssemblerLanguage
    dest_language: AssemblerLanguage
    transpile_method: Callable[[str], str]


class TranspileManager:

    def __init__(self):
        self._transpile_method_graph = PyDiGraph()
        self._language_nodes = dict()

    def register_transpile_method(self,
                                  src_language: AssemblerLanguage,
                                  dest_language: AssemblerLanguage):
        def decorator(transpile_method: Callable[[str], str]):
            self._transpile_method_graph.add_edge(
                self._get_or_create_language_node(src_language),
                self._get_or_create_language_node(dest_language),
                transpile_method
            )
            return transpile_method

        return decorator

    def _get_or_create_language_node(self, language: AssemblerLanguage):
        language_node = self._language_nodes.get(language)
        if language_node is None:
            language_node = self._transpile_method_graph.add_node(language)
            self._language_nodes[language] = language_node
        return language_node

    def _find_transpile_strategy(self,
                                 src_language: AssemblerLanguage,
                                 dest_language: AssemblerLanguage) -> list[TranspileStrategyStep]:
        dest_node = self._language_nodes[dest_language]
        paths = dijkstra_shortest_paths(
            self._transpile_method_graph,
            self._language_nodes[src_language],
            dest_node,
            default_weight=1
        )
        path_to_dest = paths[dest_node]
        if not path_to_dest:
            raise ValueError("Could not find transpile strategy")

        return [TranspileStrategyStep(
            src_language=self._transpile_method_graph.get_node_data(src),
            dest_language=self._transpile_method_graph.get_node_data(dest),
            transpile_method=self._transpile_method_graph.get_edge_data(src, dest)
        ) for src, dest in zip(path_to_dest, path_to_dest[1:])]

    def get_transpiler(self,
                       src_language: AssemblerLanguage,
                       dest_language: AssemblerLanguage):
        steps = self._find_transpile_strategy(src_language, dest_language)

        return lambda circuit: \
            reduce(lambda immediate_circuit, step: step.transpile_method(immediate_circuit), steps, circuit)

transpile_manager = TranspileManager()


@transpile_manager.register_transpile_method(AssemblerLanguage.BRAKET, AssemblerLanguage.QASM3)
def braket_to_qasm(source: Circuit) -> str:
    return source.to_ir(IRType.OPENQASM).source


@transpile_manager.register_transpile_method(AssemblerLanguage.QISKIT, AssemblerLanguage.QASM2)
def qiskit_to_qasm2(circuit: qiskit.circuit.QuantumCircuit) -> str:
    qasm = circuit.qasm()
    # TODO
    with open("C:/Users/Christoph Walcher/AppData/Local/Programs/Python/Python311/Lib/site-packages/qiskit/qasm/libs/qelib1.inc") as stdgates_file:
        stdgates = stdgates_file.read()
    qasm = qasm.replace('include "qelib1.inc";', "gate CX a,b { cnot a,b; }\n" + stdgates)
    return qasm



@transpile_manager.register_transpile_method(AssemblerLanguage.QISKIT, AssemblerLanguage.QASM3)
def qiskit_to_qasm3(circuit: qiskit.circuit.QuantumCircuit) -> str:
    print(circuit)
    qasm = qiskit.qasm3.Exporter().dumps(circuit)

    return qasm




@transpile_manager.register_transpile_method(AssemblerLanguage.QASM2, AssemblerLanguage.QISKIT)
def qasm2_to_qiskit(source: str) -> qiskit.circuit.QuantumCircuit:
    return qiskit.qasm3.loads(source)


@transpile_manager.register_transpile_method(AssemblerLanguage.QASM2, AssemblerLanguage.QISKIT)
def qasm2_to_qiskit(source: str) -> qiskit.circuit.QuantumCircuit:
    return qiskit.qasm2.loads(source)


@transpile_manager.register_transpile_method(AssemblerLanguage.QASM2, AssemblerLanguage.BRAKET)
#@transpile_manager.register_transpile_method(AssemblerLanguage.QASM3, AssemblerLanguage.BRAKET)
def qasm_to_braket(source: str) -> OpenQASMProgram:
    return OpenQASMProgram(source=source)


@transpile_manager.register_transpile_method(AssemblerLanguage.QRISP, AssemblerLanguage.QISKIT)
def qrisp_to_qiskit(circuit: qrisp.circuit.QuantumCircuit) -> OpenQASMProgram:
    from qrisp.interface.circuit_converter import convert_circuit
    return convert_circuit(circuit, "qiskit")
