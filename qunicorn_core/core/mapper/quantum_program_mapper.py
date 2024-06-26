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

from typing import Union

from qunicorn_core.api.api_models import QuantumProgramDto
from qunicorn_core.api.api_models.quantum_program_dtos import QuantumProgramRequestDto
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage


def dto_to_dataclass(quantum_program: Union[QuantumProgramDto, QuantumProgramRequestDto]) -> QuantumProgramDataclass:
    return QuantumProgramDataclass(
        assembler_language=quantum_program.assembler_language.name if quantum_program.assembler_language else None,
        quantum_circuit=quantum_program.quantum_circuit,
        python_file_path=quantum_program.python_file_path,
        python_file_metadata=quantum_program.python_file_metadata,
    )


def dataclass_to_dto(quantum_program: QuantumProgramDataclass) -> QuantumProgramDto:
    return QuantumProgramDto(
        id=quantum_program.id,
        deployment_id=quantum_program.deployment_id,
        quantum_circuit=quantum_program.quantum_circuit,
        assembler_language=(
            AssemblerLanguage(quantum_program.assembler_language) if quantum_program.assembler_language else None
        ),
        python_file_path=quantum_program.python_file_path,
        python_file_metadata=quantum_program.python_file_metadata,
    )
