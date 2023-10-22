# Copyright 2023 University of Stuttgart.
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

from enum import StrEnum


class AssemblerLanguage(StrEnum):
    """Enum to save the different assembler languages

    Values:
        QASM: Standard assembler format
        BRAKET: Assembler format from AWS
        QISKIT: Assembler format form IBM
        PYTHON: Python language for IBM File Upload
        QRISP: Assembler format from Fraunhofer
        BASIQ: Assembler format from QMWARE (Not implemented yet)
        QUIL: Assembler format from Rigetti
    """

    QASM2 = "QASM2"
    QASM3 = "QASM3"
    QRISP = "QRISP"
    BRAKET = "BRAKET"
    QISKIT = "QISKIT"
    PYTHON = "PYTHON"
    BASIQ = "BASIQ"
    QUIL = "Quil"
