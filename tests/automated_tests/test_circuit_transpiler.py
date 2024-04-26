# Copyright 2024 University of Stuttgart
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

"""test circuit transpilers"""

from qiskit import QuantumCircuit

from qunicorn_core.core.transpiler import transpile_circuit
from qunicorn_core.core.transpiler.braket_transpiler import Qasm3ToBraket, BraketToQasm3
from qunicorn_core.core.transpiler.circuit_transpiler import CircuitTranspiler
from qunicorn_core.core.transpiler.qiskit_transpiler import Qasm3ToQiskit, QiskitToQasm3


def test_no_transpile():
    circuit = QuantumCircuit()
    transpiled = transpile_circuit("QISKIT", ("QISKIT", circuit))
    assert transpiled is circuit


def test_no_transpile_multiple():
    circuit = QuantumCircuit()
    transpiled = transpile_circuit("QISKIT", ("QASM2", "test"), ("QISKIT", circuit), ("QASM3", "test2"))
    assert transpiled is circuit


def test_qasm2_roundtrip():
    circuit = QuantumCircuit(1)
    circuit.h(0)
    qasm2 = transpile_circuit("QASM2", ("QISKIT", circuit))
    assert isinstance(qasm2, str)
    assert "OPENQASM 2.0;" in qasm2
    assert "h q[0];" in qasm2
    assert "measure" not in qasm2
    transpiled = transpile_circuit("QISKIT", ("QASM2", qasm2))
    assert isinstance(transpiled, QuantumCircuit)
    assert transpiled.num_qubits == circuit.num_qubits
    for t_gate, c_gate in zip([g for g in transpiled], [g for g in circuit]):
        assert t_gate.operation.name == c_gate.operation.name
        assert len(t_gate.qubits) == len(c_gate.qubits)
        for t_qubit, c_qubit in zip(t_gate.qubits, c_gate.qubits):
            assert t_qubit.index == c_qubit.index
        assert len(t_gate.clbits) == len(c_gate.clbits)


qasm3_circuit_no_gates = """include "stdgates.inc";
    qubit[1] q;
    bit[1] c;
    measure q -> c;"""
qasm3_circuit_custom_gate = """include "stdgates.inc";
    gate majority a, b, c {
       cx c, b;
       cx c, a;
       ccx a, b, c;
    }
    qubit[3] q;
    bit[3] c;
    
    majority q[0], q[1], q[2];
    
    measure q -> c;"""
qasm3_circuit_all_std_gates = """include "stdgates.inc";
    qubit[3] q;
    bit[3] c;
    
    p(1.23) q[0];
    x q[0];
    y q[0];
    z q[0];
    h q[0];
    s q[0];
    sdg q[0];
    t q[0];
    tdg q[0];
    sx q[0];
    rx(1.23) q[0];
    ry(1.23) q[0];
    rz(1.23) q[0];
    cx q[0], q[1];
    cy q[0], q[1];
    cz q[0], q[1];
    cp(1.23) q[0], q[1];
    crx(1.23) q[0], q[1];
    cry(1.23) q[0], q[1];
    crz(1.23) q[0], q[1];
    ch q[0], q[1];
    swap q[0], q[1];
    ccx q[0], q[1], q[2];
    cswap q[0], q[1], q[2];
    cu(1.23, 2.34, 3.45, 4.56) q[0], q[1];
    CX q[0], q[1];
    phase(1.23) q[0];
    cphase(1.23) q[0], q[1];
    id q[0];
    u1(1.23) q[0];
    u2(1.23, 2.34) q[0], q[1];
    u3(1.23, 2.34, 3.45) q[0], q[1], q[2];
    
    measure q -> c;"""
qasm3_circuit_barrier = """include "stdgates.inc";
    qubit[1] q;
    bit[1] c;
    
    x q[0];
    barrier q;
    y q[0];
    
    measure q -> c;"""
qasm3_circuit_arrays = """array[int[8], 16] my_ints;
    array[float[64], 8, 4] my_doubles;
    array[uint[32], 4] my_defined_uints = {5, 6, 7, 8};
    array[float[32], 4, 2] my_defined_floats = {
        {0.5, 0.5},
        {1.0, 2.0},
        {-0.4, 0.7},
        {1.3, -2.1e-2}
    };
    array[float[32], 2] my_defined_float_row = my_defined_floats[0];
    const uint[8] DIM_SIZE = 2;
    array[int[8], DIM_SIZE, DIM_SIZE] all_ones = {{2+3, 4-1}, {3+8, 12-4}};
    uint[8] a = my_defined_uints[0];
    float[32] b = my_defined_floats[2, 1];
    my_defined_uints[1] = 5;
    my_defined_floats[3, 0] = -0.45;
    my_defined_uints[a - 1] = a + 1;
    my_defined_floats[2] = my_defined_float_row;
    my_defined_floats[0:1] = my_defined_floats[2:3];
    const uint[32] dimension = sizeof(my_defined_uints);
    const uint[32] first_dimension = sizeof(my_doubles, 0);
    const uint[32] second_dimension = sizeof(my_doubles, 1);
    const uint[32] first_dimension = sizeof(my_doubles);
    """


def test_qasm3_braket_no_gates_roundtrip():
    braket_circuit = Qasm3ToBraket().transpile_circuit(qasm3_circuit_no_gates)
    recreated_qasm3_circuit = BraketToQasm3().transpile_circuit(braket_circuit)


def test_qasm3_qiskit_no_gates_roundtrip():
    braket_circuit = Qasm3ToQiskit().transpile_circuit(qasm3_circuit_no_gates)
    recreated_qasm3_circuit = QiskitToQasm3().transpile_circuit(braket_circuit)


def test_qasm3_braket_custom_gate_roundtrip():
    braket_circuit = Qasm3ToBraket().transpile_circuit(qasm3_circuit_custom_gate)
    assert len(braket_circuit.instructions) == 3

    recreated_qasm3_circuit = BraketToQasm3().transpile_circuit(braket_circuit)


def test_qasm3_qiskit_custom_gate_roundtrip():
    braket_circuit = Qasm3ToQiskit().transpile_circuit(qasm3_circuit_custom_gate)
    recreated_qasm3_circuit = QiskitToQasm3().transpile_circuit(braket_circuit)


def test_qasm3_braket_all_std_gates_roundtrip():
    braket_circuit = Qasm3ToBraket().transpile_circuit(qasm3_circuit_all_std_gates)
    recreated_qasm3_circuit = BraketToQasm3().transpile_circuit(braket_circuit)


def test_qasm3_qiskit_all_std_gates_roundtrip():
    braket_circuit = Qasm3ToBraket().transpile_circuit(qasm3_circuit_all_std_gates)
    recreated_qasm3_circuit = BraketToQasm3().transpile_circuit(braket_circuit)


def test_qasm3_braket_barrier_roundtrip():
    braket_circuit = Qasm3ToBraket().transpile_circuit(qasm3_circuit_barrier)
    recreated_qasm3_circuit = BraketToQasm3().transpile_circuit(braket_circuit)

    assert "barrier" in recreated_qasm3_circuit


def test_qasm3_qiskit_barrier_roundtrip():
    braket_circuit = Qasm3ToQiskit().transpile_circuit(qasm3_circuit_barrier)
    recreated_qasm3_circuit = QiskitToQasm3().transpile_circuit(braket_circuit)

    assert "barrier" in recreated_qasm3_circuit


def test_qasm3_braket_arrays_roundtrip():
    braket_circuit = Qasm3ToBraket().transpile_circuit(qasm3_circuit_arrays)
    recreated_qasm3_circuit = BraketToQasm3().transpile_circuit(braket_circuit)


def test_qasm3_qiskit_arrays_roundtrip():
    braket_circuit = Qasm3ToQiskit().transpile_circuit(qasm3_circuit_arrays)
    recreated_qasm3_circuit = QiskitToQasm3().transpile_circuit(braket_circuit)


def test_connectivity():
    """Assert that all formats can be transpiled to all other formats."""

    # use this to set exeptions to full connectivity
    known_partially_connected = {"QISKIT-PYTHON", "BRAKET-PYTHON", "QRISP-PYTHON", "QUIL-PYTHON", "QUIL"}

    formats = CircuitTranspiler.get_known_formats()

    full_connectivity = formats - known_partially_connected

    known_full_connectivity = set()

    missing_connections = {}

    def is_fully_connected(format_):
        connectivity = {format_}  # set for all reachable formats
        explored = set()  # set for all already expanded formats
        while explored != connectivity:  # all reachable formats expanded
            for source in connectivity - explored:  # all not expanded formats
                explored.add(source)
                for transpiler in CircuitTranspiler.get_transpilers(source):
                    connectivity.add(transpiler.target)
                if not known_full_connectivity.isdisjoint(connectivity):
                    # at least one already known fully connected format was reached
                    return True
        if connectivity >= full_connectivity:
            return True
        else:
            missing_connections[format_] = full_connectivity - connectivity
            return False

    for format_ in formats:
        if is_fully_connected(format_):
            known_full_connectivity.add(format_)

    missing = "\n".join((f"{source}: " + ", ".join(targets)) for source, targets in missing_connections.items())

    assert known_full_connectivity >= full_connectivity, f"Missing connections:\n {missing}"
