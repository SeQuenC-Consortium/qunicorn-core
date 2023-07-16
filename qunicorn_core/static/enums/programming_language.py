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


class ProgrammingLanguage(StrEnum):
    """Enum to save the different programming languages for quantum circuits

    Values:
        QISKIT: The programming language is QISKIT
        PYQUIL: The programming language is PYQUIL
        QMWARE: The programming language is QMWARE
        QRISP: Assembler format from Frauenhofer
        BASIQ: Assembler format from QMWARE
    """

    QISKIT = "QISKIT"
    PYQUIL = "PYQUIL"
    QMWARE = "QMWARE"
    QRISP = "QRISP"
    BASIQ = "BASIQ"
    BRAKET = "BRAKET"
