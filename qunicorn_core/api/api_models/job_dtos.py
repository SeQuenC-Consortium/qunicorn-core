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


"""Module containing all Dtos and their Schemas for tasks in the Jobmanager API."""
import typing
from dataclasses import dataclass
from datetime import datetime

import marshmallow as ma
from marshmallow import fields, ValidationError

from .deployment_dtos import DeploymentDto
from .device_dtos import DeviceDto, DeviceDtoSchema
from .quantum_program_dtos import QuantumProgramDto
from .result_dtos import ResultDto
from .user_dtos import UserDto, UserDtoSchema
from ..flask_api_utils import MaBaseSchema

__all__ = [
    "SimpleJobDtoSchema",
    "SimpleJobDto",
    "JobResponseDtoSchema",
    "JobRequestDtoSchema",
    "JobCoreDto",
    "JobResponseDto",
    "JobRequestDto",
]

from ...static.enums.assembler_languages import AssemblerLanguage

from ...static.enums.job_state import JobState
from ...static.enums.job_type import JobType
from ...static.enums.provider_name import ProviderName
from ...util import utils


@dataclass
class JobRequestDto:
    """JobDto that was sent from the user as a request"""

    name: str
    provider_name: str
    device_name: str
    shots: int
    parameters: str
    token: str
    type: JobType
    assembler_language: AssemblerLanguage
    programs: typing.List["QuantumProgramDto"] | None = None
    circuits: list[str] | None = None

    @staticmethod
    def from_dict(body: dict) -> "JobRequestDto":
        job_dto: JobRequestDto = JobRequestDto(**body)
        job_dto.programs = [QuantumProgramDto(**program) for program in body["programs"]]
        return job_dto


@dataclass
class JobCoreDto:
    """JobDto that is used for all internal job handling"""

    id: int
    executed_by: UserDto
    executed_on: DeviceDto
    deployment: DeploymentDto
    progress: str
    state: JobState
    shots: int
    type: JobType
    started_at: datetime
    finished_at: datetime
    name: str
    data: str
    results: list[ResultDto]
    parameters: str
    ibm_file_options: dict | None = None
    ibm_file_inputs: dict | None = None
    token: str | None = None


@dataclass
class JobResponseDto:
    """JobDto that is sent to the user as a response"""

    id: int
    executed_by: UserDto
    executed_on: DeviceDto
    progress: str
    state: str
    type: JobType
    started_at: datetime
    finished_at: datetime
    name: str
    data: str
    results: list[ResultDto]
    parameters: str


@dataclass
class SimpleJobDto:
    id: int
    name: str
    job_state: JobState = JobState.RUNNING


@dataclass
class JobExecutionDto:
    token: str | None = None
    python_file_options: str | None = None
    python_file_inputs: str | None = None


class CircuitField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) or isinstance(value, list):
            return value
        else:
            raise ValidationError("Field should be str or list")


class JobRequestDtoSchema(MaBaseSchema):
    name = ma.fields.String(required=True, example="JobName")
    circuits = CircuitField(required=True, example=[utils.get_default_qasm_string(), utils.get_default_qasm_string(2)])
    programs = ma.fields.Nested("QuantumProgramSchema", many=True)
    provider_name = ma.fields.Enum(required=True, example=ProviderName.IBM, enum=ProviderName)
    device_name = ma.fields.String(required=True, example="aer_simulator")
    shots = ma.fields.Int(
        required=False,
        allow_none=True,
        metadata={
            "label": "Shots",
            "description": "Number of shots",
            "input_type": "number",
        },
        example=4000,
    )
    parameters = ma.fields.List(ma.fields.Float(), required=False)
    token = ma.fields.String(required=True, example="")
    type = ma.fields.Enum(required=True, example=JobType.RUNNER, enum=JobType)
    assembler_language = ma.fields.Enum(required=True, example=AssemblerLanguage.QASM, enum=AssemblerLanguage)


class JobResponseDtoSchema(MaBaseSchema):
    id = ma.fields.Int(required=True, dump_only=True)
    executed_by = UserDtoSchema()
    executed_on = DeviceDtoSchema()
    progress = ma.fields.Int(required=True, dump_only=True)
    state = ma.fields.String(required=True, dump_only=True)
    type = ma.fields.String(required=True, dump_only=True)
    started_at = ma.fields.String(required=True, dump_only=True)
    finished_at = ma.fields.String(required=True, dump_only=True)
    data = ma.fields.String(required=True, dump_only=True)
    results = ma.fields.List(ma.fields.Dict(), required=True, dump_only=True)
    parameters = ma.fields.String(required=True, dump_only=True)


class SimpleJobDtoSchema(MaBaseSchema):
    id = ma.fields.Integer(required=True, allow_none=False, dump_only=True)
    job_name = ma.fields.String(required=False, allow_none=False, dump_only=True)
    job_state = ma.fields.String(required=False, allow_none=False, dump_only=True)


class JobExecutionDtoSchema(MaBaseSchema):
    token = ma.fields.String(required=True, example="")
    python_file_options = ma.fields.Dict(required=True, example={"backend": "ibmq_qasm_simulator"})
    python_file_inputs = ma.fields.Dict(required=True)
