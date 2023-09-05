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
from datetime import datetime

from qunicorn_core.api.api_models.job_dtos import (
    JobCoreDto,
    JobRequestDto,
    JobResponseDto,
    SimpleJobDto,
)
from qunicorn_core.api.api_models.user_dtos import UserDto
from qunicorn_core.core.mapper import deployment_mapper, device_mapper, user_mapper, result_mapper
from qunicorn_core.core.mapper.general_mapper import map_from_to
from qunicorn_core.db.database_services import device_db_service, deployment_db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState


def request_to_core(job: JobRequestDto):
    # Get the objects from the database by its ids
    device: DeviceDataclass = device_db_service.get_device_by_name(job.device_name)
    deployment: DeploymentDataclass = deployment_db_service.get_deployment_by_id(job.deployment_id)

    return map_from_to(
        from_object=job,
        to_type=JobCoreDto,
        fields_mapping={
            "executed_by": UserDto.get_default_user(),
            "executed_on": device_mapper.dataclass_to_dto(device),
            "deployment": deployment_mapper.dataclass_to_dto(deployment),
            "progress": 0,
            "state": JobState.READY,
            "started_at": datetime.now(),
            "results": [],
        },
    )


def core_to_response(job: JobCoreDto) -> JobResponseDto:
    return map_from_to(job, JobResponseDto)


def dataclass_to_response(job: JobDataclass) -> JobResponseDto | None:
    return map_from_to(
        from_object=job,
        to_type=JobResponseDto,
        fields_mapping={
            "executed_by": user_mapper.dataclass_to_dto(job.executed_by),
            "executed_on": device_mapper.dataclass_to_dto(job.executed_on),
            "results": [result_mapper.dataclass_to_dto(result) for result in job.results],
        },
    )


def core_to_dataclass(job: JobCoreDto) -> JobDataclass:
    return map_from_to(
        from_object=job,
        to_type=JobDataclass,
        fields_mapping={
            "executed_by": user_mapper.dto_to_dataclass(job.executed_by),
            "executed_on": device_mapper.dto_to_dataclass(job.executed_on),
            "deployment": deployment_mapper.dto_to_dataclass(job.deployment),
            "parameters": str(job.parameters),
        },
    )


def dataclass_to_core(job: JobDataclass) -> JobCoreDto:
    return map_from_to(
        from_object=job,
        to_type=JobCoreDto,
        fields_mapping={
            "executed_by": user_mapper.dataclass_to_dto(job.executed_by),
            "executed_on": device_mapper.dataclass_to_dto(job.executed_on),
            "deployment": deployment_mapper.dataclass_to_dto(job.deployment),
            "results": [result_mapper.dataclass_to_dto(result) for result in job.results],
        },
    )


def dataclass_to_request(job: JobDataclass) -> JobRequestDto:
    return map_from_to(
        from_object=job,
        to_type=JobRequestDto,
        fields_mapping={
            "provider_name": job.executed_on.provider.name,
            "token": "",
            "deployment_id": job.deployment.id,
            "device_name": job.executed_on.device_name,
        },
    )


def dataclass_to_simple(job: JobDataclass) -> SimpleJobDto:
    return map_from_to(job, SimpleJobDto)
