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

from .deployment_dtos import DeploymentDto
from .device_dtos import DeviceDto, DeviceDtoSchema
from .result_dtos import ResultDto, ResultDtoSchema
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
    "TokenSchema",
    "JobExecutePythonFileDto",
    "JobExecutionDtoSchema",
]

from ...static.enums.job_state import JobState
from ...static.enums.job_type import JobType
from ...static.enums.provider_name import ProviderName


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
    deployment_id: int


@dataclass
class JobCoreDto:
    """JobDto that is used for all internal job handling"""

    executed_by: UserDto
    executed_on: DeviceDto
    deployment: DeploymentDto
    progress: int
    state: JobState
    shots: int
    type: JobType
    started_at: datetime
    name: str
    results: list[ResultDto]
    id: int | None = None
    parameters: str | None = None
    data: str | None = None
    finished_at: datetime | None = None
    ibm_file_options: dict | None = None
    ibm_file_inputs: dict | None = None
    token: str | None = None

    # TODO: check if datatype is accuarte
    provider_specific_id: str | None = None


@dataclass
class JobResponseDto:
    """JobDto that is sent to the user as a response"""

    id: int
    executed_by: UserDto
    executed_on: DeviceDto
    progress: int
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
    state: JobState = JobState.RUNNING


@dataclass
class JobExecutePythonFileDto:
    token: str | None = None
    python_file_options: str | None = None
    python_file_inputs: str | None = None


class JobRequestDtoSchema(MaBaseSchema):
    name = ma.fields.String(required=True, metadata={"example": "JobName"})
    provider_name = ma.fields.Enum(required=True, metadata={"example": ProviderName.IBM}, enum=ProviderName)
    device_name = ma.fields.String(required=True, metadata={"example": "aer_simulator"})
    shots = ma.fields.Int(
        required=False,
        allow_none=True,
        metadata={"example": 4000, "label": "shots", "description": "number of shots", "input_type": "number"},
    )
    parameters = ma.fields.List(ma.fields.Float(), required=False)
    token = ma.fields.String(required=True, metadata={"example": ""})
    type = ma.fields.Enum(required=True, metadata={"example": JobType.RUNNER}, enum=JobType)
    deployment_id = ma.fields.Integer(required=False, allow_none=True, metadata={"example": 1})


class JobResponseDtoSchema(MaBaseSchema):
    id = ma.fields.Int(required=True, dump_only=True)
    executed_by = ma.fields.Nested(UserDtoSchema())
    executed_on = ma.fields.Nested(DeviceDtoSchema())
    progress = ma.fields.Int(required=True, dump_only=True)
    state = ma.fields.String(required=True, dump_only=True)
    type = ma.fields.String(required=True, dump_only=True)
    started_at = ma.fields.String(required=True, dump_only=True)
    finished_at = ma.fields.String(required=True, dump_only=True)
    data = ma.fields.String(required=True, dump_only=True)
    results = ma.fields.Nested(ResultDtoSchema(), many=True, required=True, dump_only=True)
    parameters = ma.fields.String(required=True, dump_only=True)


class SimpleJobDtoSchema(MaBaseSchema):
    id = ma.fields.Integer(required=True, allow_none=False, dump_only=True)
    job_name = ma.fields.String(required=False, allow_none=False, dump_only=True)
    job_state = ma.fields.String(required=False, allow_none=False, dump_only=True)


class TokenSchema(MaBaseSchema):
    token = ma.fields.String(required=True, metadata={"example": ""})


class JobExecutionDtoSchema(MaBaseSchema):
    token = ma.fields.String(required=True, metadata={"example": ""})
    python_file_options = ma.fields.Dict(required=True, metadata={"example": {"backend": "ibmq_qasm_simulator"}})
    python_file_inputs = ma.fields.Dict(required=True)
