# Copyright 2023 University of Stuttgart
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import dataclasses
from functools import reduce
from os import path
from typing import Any, Callable, Dict, Sequence, Union

import qiskit.circuit
import qiskit.qasm2
import qiskit.qasm3
import qrisp.circuit
from braket.circuits import Circuit
from braket.circuits.serialization import IRType
from braket.ir.openqasm import Program as OpenQASMProgram
from pyquil import Program, get_qc
from qrisp.interface.circuit_converter import convert_circuit
from rustworkx import PyDiGraph, digraph_dijkstra_shortest_paths
from rustworkx.visualization import graphviz_draw

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.qunicorn_exception import QunicornError
from qunicorn_core.util import logging, utils

"""
Data class for each step when transpiling from a source language to the destination language
"""


@dataclasses.dataclass
class TranspileStrategyStep:
    src_language: str
    dest_language: str
    transpile_method: Callable[[str], str]


"""
Class that handles all transpiling between different assembler languages

The different languages are implemented as nodes and the shortest route is used to find the required transpiling steps
"""


class TranspileManager:
    def __init__(self):
        self._transpile_method_graph: PyDiGraph[str, Callable[[Any], Any]] = PyDiGraph()
        self._language_nodes: Dict[str, Any] = dict()

    def register_transpile_method(
        self, src_language: Union[AssemblerLanguage, str], dest_language: Union[AssemblerLanguage, str]
    ):
        """Decorator to define the transpile method from a Node A (source language) to Node B (destination language)"""

        if isinstance(src_language, AssemblerLanguage):
            src_language = src_language.value
        if isinstance(dest_language, AssemblerLanguage):
            dest_language = dest_language.value

        def decorator(transpile_method: Callable[[Any], Any]):
            self._transpile_method_graph.add_edge(
                self._get_or_create_language_node(src_language),
                self._get_or_create_language_node(dest_language),
                transpile_method,
            )
            return transpile_method

        return decorator

    def _get_or_create_language_node(self, language: str) -> int:
        language_node = self._language_nodes.get(language)
        if language_node is None:
            language_node = self._transpile_method_graph.add_node(language)
            self._language_nodes[language] = language_node
        return language_node

    def _find_transpile_strategy(self, src_language: str, dest_language: str) -> list[TranspileStrategyStep]:
        """Transpile strategy is selected from a graph with a node for each language by using the dijkstra algorithm"""
        dest_node = self._language_nodes[dest_language]
        paths = digraph_dijkstra_shortest_paths(
            self._transpile_method_graph, self._language_nodes[src_language], dest_node, default_weight=1
        )
        path_to_dest = paths[dest_node]
        if not path_to_dest:
            raise QunicornError("Could not find transpile strategy")

        return [
            TranspileStrategyStep(
                src_language=self._transpile_method_graph.get_node_data(src),
                dest_language=self._transpile_method_graph.get_node_data(dest),
                transpile_method=self._transpile_method_graph.get_edge_data(src, dest),
            )
            for src, dest in zip(path_to_dest, path_to_dest[1:])
        ]

    def get_transpiler(self, src_language: str, dest_languages: Sequence[str]) -> Any:
        """Main method of the class that returns the method to be used to transpile to the destination language"""
        steps = None
        # in case of multiple supported languages the shortest path is selected by comparing the options
        for dest_language in dest_languages:
            steps_of_current_run = self._find_transpile_strategy(src_language, dest_language)
            if steps is None or len(steps_of_current_run) < len(steps):
                steps = steps_of_current_run

        if steps is None:
            raise QunicornError(
                f"Could not find a transpilation path from {src_language} to any of the supported languages {', '.join(dest_languages)}!"  # noqa: E501, W505
            )

        def transpile(circuit) -> Any:
            """This method transpiles the circuit from the source language to the destination language by using
            intermediate circuits along the discovered shortest path (saved in "steps"). It iteratively applies
            the transpile methods from the selected steps to return one single transpiled circuit.
            The result of one iteration becomes the immediate_circuit/input for the next iteration."""
            return reduce(lambda immediate_circuit, step: step.transpile_method(immediate_circuit), steps, circuit)

        return transpile

    def visualize_transpile_strategy(self, filename):
        """Visualisation of the graph of the possible transpile methods between each node"""
        graphviz_draw(
            self._transpile_method_graph, node_attr_fn=lambda language: {"label": str(language)}, filename=filename
        )


transpile_manager = TranspileManager()


@transpile_manager.register_transpile_method(AssemblerLanguage.BRAKET, AssemblerLanguage.QASM3)
def braket_to_qasm3(source: Circuit) -> str:
    return source.to_ir(IRType.OPENQASM).source


@transpile_manager.register_transpile_method(AssemblerLanguage.QISKIT, AssemblerLanguage.QASM2)
def qiskit_to_qasm2(circuit: qiskit.circuit.QuantumCircuit) -> str:
    qasm = circuit.qasm()
    # replace gate references standard gate library an add 'CX' to 'cnot' mapping
    with open(path.join(path.dirname(qiskit.__file__), "qasm/libs/qelib1.inc")) as qelib1_file:
        qelib1 = qelib1_file.read()
        qasm = qasm.replace('include "qelib1.inc";', "gate CX a,b { cnot a,b; }\n" + qelib1)
    return qasm


@transpile_manager.register_transpile_method(AssemblerLanguage.QISKIT, AssemblerLanguage.QASM3)
def qiskit_to_qasm3(circuit: qiskit.circuit.QuantumCircuit) -> str:
    qasm = qiskit.qasm3.Exporter(allow_aliasing=False).dumps(circuit)
    # replace gate references standard gate library
    with open(path.join(path.dirname(qiskit.__file__), "qasm/libs/stdgates.inc")) as stdgates_file:
        stdgates = stdgates_file.read()
    qasm = qasm.replace('include "stdgates.inc";', stdgates)
    return qasm


@transpile_manager.register_transpile_method(AssemblerLanguage.QASM3, AssemblerLanguage.QISKIT)
def qasm3_to_qiskit(source: str) -> qiskit.circuit.QuantumCircuit:
    source = source.replace("cnot", "cx")

    # heuristic to check for missing import
    if '"stdgates.inc"' not in source:
        # try to add stdgates import if it is missing
        # only one of the following replace is executed since it can only find either one , but both are valid strings
        source = source.replace("OPENQASM 3;", 'OPENQASM 3; include "stdgates.inc";')
        source = source.replace("OPENQASM 3.0;", 'OPENQASM 3.0; include "stdgates.inc";')
    return qiskit.qasm3.loads(source)


@transpile_manager.register_transpile_method(AssemblerLanguage.QASM2, AssemblerLanguage.QISKIT)
def qasm2_to_qiskit(source: str) -> qiskit.circuit.QuantumCircuit:
    return qiskit.qasm2.loads(source)


@transpile_manager.register_transpile_method(AssemblerLanguage.QASM3, AssemblerLanguage.BRAKET)
def qasm3_to_braket(source: str) -> OpenQASMProgram:
    return OpenQASMProgram(source=source)


@transpile_manager.register_transpile_method(AssemblerLanguage.QRISP, AssemblerLanguage.QISKIT)
def qrisp_to_qiskit(circuit: qrisp.circuit.QuantumCircuit) -> OpenQASMProgram:
    return convert_circuit(circuit, "qiskit")


@transpile_manager.register_transpile_method(AssemblerLanguage.QASM2, AssemblerLanguage.QUIL)
def qasm2_to_quil(source: str) -> Program:
    # qvm and quilc from pyquil should run in server mode and can be found with get_qc
    # WARNING: the qasm to quil transpilation does not allow for the use of standard gate library.
    if not utils.is_experimental_feature_enabled():
        raise QunicornError(
            "Experimental transpilation features are disabled, set ENABLE_EXPERIMENTAL_TRANSPILATION to true to enable them.",  # noqa: E501
            405,
        )
    logging.warn("This function is experimental and could not be fully tested yet. ")
    quilc_compiler = get_qc("9q-square-qvm").compiler
    return quilc_compiler.transpile_qasm_2(source)
