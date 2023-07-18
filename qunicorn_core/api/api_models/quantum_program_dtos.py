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


"""Module containing all Dtos and their Schemas  for tasks in the QuantumProgram API."""
from dataclasses import dataclass
import marshmallow as ma

__all__ = ["QuantumProgramDto", "QuantumProgramSchema"]

from qunicorn_core.api.flask_api_utils import MaBaseSchema
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage


@dataclass
class QuantumProgramDto:
    id: int | None = None
    quantum_circuit: str | None = None
    assembler_language: AssemblerLanguage | None = None
    python_file_path: str | None = None
    python_file_metadata: str | None = None


class QuantumProgramSchema(MaBaseSchema):
    quantum_circuit = ma.fields.String(required=False, allow_none=True)
    assembler_language = ma.fields.Enum(required=True, example=AssemblerLanguage.QASM, enum=AssemblerLanguage)
    python_file_path = ma.fields.String(required=False, example="test.py", allow_none=True)
    python_file_metadata = ma.fields.String(required=False, example="test.json", eallow_none=True)
