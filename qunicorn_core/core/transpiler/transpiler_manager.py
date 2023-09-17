import dataclasses
from functools import reduce
from os import path
from typing import Callable

import qiskit.circuit
import qiskit.qasm2
import qiskit.qasm3
from braket.circuits import Circuit
from braket.circuits.serialization import IRType
from braket.ir.openqasm import Program as OpenQASMProgram
from rustworkx import PyDiGraph, digraph_dijkstra_shortest_paths
from rustworkx.visualization import graphviz_draw

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage

"""Class that handles all transpiling between different assembler languages"""


@dataclasses.dataclass
class TranspileStrategyStep:
    src_language: AssemblerLanguage
    dest_language: AssemblerLanguage
    transpile_method: Callable[[str], str]


class TranspileManager:
    def __init__(self):
        self._transpile_method_graph = PyDiGraph()
        self._language_nodes = dict()

    def register_transpile_method(self, src_language: AssemblerLanguage, dest_language: AssemblerLanguage):
        def decorator(transpile_method: Callable[[str], str]):
            self._transpile_method_graph.add_edge(
                self._get_or_create_language_node(src_language),
                self._get_or_create_language_node(dest_language),
                transpile_method,
            )
            return transpile_method

        return decorator

    def _get_or_create_language_node(self, language: AssemblerLanguage):
        language_node = self._language_nodes.get(language)
        if language_node is None:
            language_node = self._transpile_method_graph.add_node(language)
            self._language_nodes[language] = language_node
        return language_node

    def _find_transpile_strategy(
        self, src_language: AssemblerLanguage, dest_language: AssemblerLanguage
    ) -> list[TranspileStrategyStep]:
        dest_node = self._language_nodes[dest_language]
        paths = digraph_dijkstra_shortest_paths(
            self._transpile_method_graph, self._language_nodes[src_language], dest_node, default_weight=1
        )
        path_to_dest = paths[dest_node]
        if not path_to_dest:
            raise ValueError("Could not find transpile strategy")

        return [
            TranspileStrategyStep(
                src_language=self._transpile_method_graph.get_node_data(src),
                dest_language=self._transpile_method_graph.get_node_data(dest),
                transpile_method=self._transpile_method_graph.get_edge_data(src, dest),
            )
            for src, dest in zip(path_to_dest, path_to_dest[1:])
        ]

    def get_transpiler(self, src_language: AssemblerLanguage, dest_languages: [AssemblerLanguage]):
        steps = None
        # in case of multiple supported languages the shortest path is selected
        for dest_language in dest_languages:
            steps_of_current_run = self._find_transpile_strategy(src_language, dest_language)
            if steps is None or len(steps_of_current_run) < len(steps):
                steps = steps_of_current_run

        def transpile(circuit):
            return reduce(lambda immediate_circuit, step: step.transpile_method(immediate_circuit), steps, circuit)

        return transpile

    def visualize_transpile_strategy(self, filename):
        graphviz_draw(
            self._transpile_method_graph, node_attr_fn=lambda language: {"label": str(language)}, filename=filename
        )


transpile_manager = TranspileManager()


@transpile_manager.register_transpile_method(AssemblerLanguage.BRAKET, AssemblerLanguage.QASM3)
def braket_to_qasm(source: Circuit) -> str:
    return source.to_ir(IRType.OPENQASM).source


@transpile_manager.register_transpile_method(AssemblerLanguage.QISKIT, AssemblerLanguage.QASM2)
def qiskit_to_qasm2(circuit: qiskit.circuit.QuantumCircuit) -> str:
    qasm = circuit.qasm()
    # XXX replace gate references standard gate library an add 'CX' to 'cnot' mapping
    with open(path.join(path.dirname(qiskit.__file__), "qasm/libs/qelib1.inc")) as qelib1_file:
        qelib1 = qelib1_file.read()
        qasm = qasm.replace('include "qelib1.inc";', "gate CX a,b { cnot a,b; }\n" + qelib1)
    return qasm


@transpile_manager.register_transpile_method(AssemblerLanguage.QISKIT, AssemblerLanguage.QASM3)
def qiskit_to_qasm3(circuit: qiskit.circuit.QuantumCircuit) -> str:
    qasm = qiskit.qasm3.Exporter(allow_aliasing=False).dumps(circuit)
    # XXX replace gate references standard gate library
    with open(path.join(path.dirname(qiskit.__file__), "qasm/libs/stdgates.inc")) as stdgates_file:
        stdgates = stdgates_file.read()
    qasm = qasm.replace('include "stdgates.inc";', stdgates)
    return qasm


@transpile_manager.register_transpile_method(AssemblerLanguage.QASM3, AssemblerLanguage.QISKIT)
def qasm3_to_qiskit(source: str) -> qiskit.circuit.QuantumCircuit:
    source = source.replace("cnot", "cx")
    # only one of the following replace is executed since it can only find either one , but both are valid strings
    source = source.replace("OPENQASM 3;", 'OPENQASM 3; include "stdgates.inc";')
    source = source.replace("OPENQASM 3.0;", 'OPENQASM 3.0; include "stdgates.inc";')
    return qiskit.qasm3.loads(source)


@transpile_manager.register_transpile_method(AssemblerLanguage.QASM2, AssemblerLanguage.QISKIT)
def qasm2_to_qiskit(source: str) -> qiskit.circuit.QuantumCircuit:
    return qiskit.qasm2.loads(source)


# @transpile_manager.register_transpile_method(AssemblerLanguage.QASM2, AssemblerLanguage.BRAKET)
@transpile_manager.register_transpile_method(AssemblerLanguage.QASM3, AssemblerLanguage.BRAKET)
def qasm_to_braket(source: str) -> OpenQASMProgram:
    return OpenQASMProgram(source=source)
