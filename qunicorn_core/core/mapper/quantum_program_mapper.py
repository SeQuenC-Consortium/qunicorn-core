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

from qunicorn_core.api.api_models import QuantumProgramDto
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass


def quantum_program_dto_to_quantum_program(quantum_program: QuantumProgramDto) -> QuantumProgramDataclass:
    return QuantumProgramDataclass(id=quantum_program.id, quantum_circuit=quantum_program.quantum_circuit)


def quantum_program_to_quantum_program_dto(quantum_program: QuantumProgramDataclass) -> QuantumProgramDto:
    return QuantumProgramDto(id=quantum_program.id, quantum_circuit=quantum_program.quantum_circuit)