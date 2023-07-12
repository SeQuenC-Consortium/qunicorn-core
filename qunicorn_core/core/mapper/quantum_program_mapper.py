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
import json

from qunicorn_core.api.api_models import QuantumProgramDto
from qunicorn_core.db.database_services import quantum_program_db_service
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass


def dto_to_quantum_program(quantum_program: QuantumProgramDto) -> QuantumProgramDataclass:
    program: QuantumProgramDataclass = quantum_program_db_service.get_program(quantum_program.id)
    if program is not None:
        program.quantum_circuit = quantum_program.quantum_circuit
        program.assembler_language = quantum_program.assembler_language
        program.python_file_path = quantum_program.python_file_path
        program.python_file_metadata = quantum_program.python_file_metadata
        program.python_file_options = quantum_program.python_file_options
        program.python_file_inputs = quantum_program.python_file_inputs
    return program


def dto_to_quantum_program_without_id(quantum_program: QuantumProgramDto) -> QuantumProgramDataclass:
    return QuantumProgramDataclass(
        quantum_circuit=quantum_program.quantum_circuit,
        assembler_language=quantum_program.assembler_language,
        python_file_path=quantum_program.python_file_path,
        python_file_metadata=quantum_program.python_file_metadata,
        python_file_options=json.dumps(quantum_program.python_file_options),
        python_file_inputs=json.dumps(quantum_program.python_file_inputs),
    )


def quantum_program_to_dto(quantum_program: QuantumProgramDataclass) -> QuantumProgramDto:
    return QuantumProgramDto(
        id=quantum_program.id,
        quantum_circuit=quantum_program.quantum_circuit,
        assembler_language=quantum_program.assembler_language,
        python_file_path=quantum_program.python_file_path,
        python_file_metadata=quantum_program.python_file_metadata,
        python_file_options=quantum_program.python_file_options,
        python_file_inputs=quantum_program.python_file_inputs,
    )
