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
from dataclasses import dataclass
from datetime import datetime

import marshmallow as ma
from marshmallow import fields, ValidationError
from qiskit import QuantumCircuit

from .deployment_dtos import DeploymentDto
from .device_dtos import DeviceDto, DeviceDtoSchema
from .user_dtos import UserDto, UserDtoSchema
from ..util import MaBaseSchema

__all__ = [
    "SimpleJobDtoSchema",
    "SimpleJobDto",
    "JobResponseDtoSchema",
    "JobRequestDtoSchema",
    "JobCoreDto",
    "JobResponseDto",
    "JobRequestDto",
    "JobPostRequestTypesSchema",
]

from ...static.enums.assembler_languages import AssemblerLanguage

from ...static.enums.job_state import JobState
from ...static.enums.provider_name import ProviderName


@dataclass
class JobRequestDto:
    """JobDto that was sent from the user as a request"""

    name: str
    circuit: str
    provider_name: str
    shots: int
    parameters: str
    token: str
    assembler_language: AssemblerLanguage


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
    started_at: datetime
    finished_at: datetime
    name: str
    data: str
    results: str
    parameters: str
    token: str | None = None


@dataclass
class JobResponseDto:
    """JobDto that is sent to the user as a response"""

    id: int
    executed_by: UserDto
    executed_on: DeviceDto
    progress: str
    state: str
    started_at: datetime
    finished_at: datetime
    name: str
    data: str
    results: str
    parameters: str


@dataclass
class SimpleJobDto:
    id: str
    name: str
    job_state: JobState = JobState.RUNNING


class CircuitField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) or isinstance(value, list):
            return value
        else:
            raise ValidationError("Field should be str or list")


def get_quasm_string() -> str:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc.qasm()


class JobRequestDtoSchema(MaBaseSchema):
    name = ma.fields.String(required=True, example="JobName")
    circuit = CircuitField(required=True, example=get_quasm_string())
    provider_name = ma.fields.Enum(required=True, example=ProviderName.IBM, enum=ProviderName)
    shots = ma.fields.Int(
        required=False,
        allow_none=True,
        metada={
            "label": "Shots",
            "description": "Number of shots",
            "input_type": "number",
        },
        example=4000,
    )
    parameters = ma.fields.List(ma.fields.Float(), required=False)
    token = ma.fields.String(required=True, example="")
    assembler_language = ma.fields.Enum(required=True, example=AssemblerLanguage.QASM, enum=AssemblerLanguage)


class JobPostRequestTypesSchema(MaBaseSchema):
    postReqTyp = ma.fields.String(required=True, example="-cancel/-run/-pause")


class JobResponseDtoSchema(MaBaseSchema):
    id = ma.fields.Int(required=True, dump_only=True)
    executed_by = UserDtoSchema()
    executed_on = DeviceDtoSchema()
    progress = ma.fields.Int(required=True, dump_only=True)
    state = ma.fields.String(required=True, dump_only=True)
    started_at = ma.fields.String(required=True, dump_only=True)
    finished_at = ma.fields.String(required=True, dump_only=True)
    data = ma.fields.String(required=True, dump_only=True)
    results = ma.fields.String(required=True, dump_only=True)
    parameters = ma.fields.String(required=True, dump_only=True)


class SimpleJobDtoSchema(MaBaseSchema):
    id = ma.fields.Integer(required=True, allow_none=False, dump_only=True, example=123)
    job_name = ma.fields.String(required=False, allow_none=False, dump_only=True)
    job_state = ma.fields.String(required=False, allow_none=False, dump_only=True)
