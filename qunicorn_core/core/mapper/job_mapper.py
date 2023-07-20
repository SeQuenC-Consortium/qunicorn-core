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

from qunicorn_core.api.api_models import ProviderDto
from qunicorn_core.api.api_models.device_dtos import DeviceDto
from qunicorn_core.api.api_models.job_dtos import (
    JobCoreDto,
    JobRequestDto,
    JobResponseDto,
    SimpleJobDto,
)
from qunicorn_core.api.api_models.user_dtos import UserDto
from qunicorn_core.core.mapper import deployment_mapper, device_mapper, user_mapper, result_mapper
from qunicorn_core.db.database_services import db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.programming_language import ProgrammingLanguage


def request_to_core(job: JobRequestDto):
    """Helper class. When the db objects are saved correctly we do not need it anymore"""
    provider = ProviderDto(id=0, with_token=True, supported_language=ProgrammingLanguage.QISKIT, name=job.provider_name)
    device = DeviceDto(id=0, device_name=job.device_name, provider=provider, url="DefaultUrl")

    # Get deployment from db and map to dto
    deployment: DeploymentDataclass = db_service.get_database_object(job.deployment_id, DeploymentDataclass)
    deployment_dto = deployment_mapper.deployment_to_deployment_dto(deployment)

    return JobCoreDto(
        id=None,
        executed_by=UserDto.get_default_user(),
        executed_on=device,
        deployment=deployment_dto,
        token=job.token,
        name=job.name,
        parameters=job.parameters,
        progress=str(0),
        state=JobState.READY,
        shots=job.shots,
        type=job.type,
        started_at=datetime.now(),
        finished_at=datetime.now(),
        data="",
        results=[],
    )


def core_to_response(job: JobCoreDto) -> JobResponseDto:
    return JobResponseDto(
        id=job.id,
        executed_by=job.executed_by,
        executed_on=job.executed_on,
        progress=job.progress,
        state=job.state,
        type=job.type,
        started_at=job.started_at,
        finished_at=job.finished_at,
        name=job.name,
        data=job.data,
        results=job.results,
        parameters=job.parameters,
    )


def job_to_response(job: JobDataclass) -> JobResponseDto:
    return JobResponseDto(
        id=job.id,
        executed_by=user_mapper.user_to_user_dto(job.executed_by),
        executed_on=device_mapper.device_to_device_dto(job.executed_on),
        progress=str(job.progress),
        state=job.state,
        type=job.type,
        started_at=job.started_at,
        finished_at=job.finished_at,
        name=job.name,
        data=job.data,
        results=job.results,
        parameters=job.parameters,
    )


def job_core_dto_to_job(job: JobCoreDto) -> JobDataclass:
    return JobDataclass(
        id=job.id,
        executed_by=user_mapper.user_dto_to_user(job.executed_by),
        executed_on=device_mapper.device_dto_to_device(job.executed_on),
        deployment=deployment_mapper.deployment_dto_to_deployment(job.deployment),
        progress=job.progress,
        state=job.state,
        shots=job.shots,
        type=job.type,
        started_at=job.started_at,
        finished_at=job.finished_at,
        name=job.name,
        data=job.data,
        results=job.results,
        parameters=str(job.parameters),
    )


def job_core_dto_to_job_without_id(job: JobCoreDto) -> JobDataclass:
    return JobDataclass(
        executed_by=user_mapper.user_dto_to_user_without_id(job.executed_by),
        executed_on=device_mapper.device_dto_to_device_without_id(job.executed_on),
        deployment=deployment_mapper.deployment_dto_to_deployment(job.deployment),
        progress=job.progress,
        state=job.state,
        shots=job.shots,
        type=job.type,
        started_at=job.started_at,
        finished_at=job.finished_at,
        name=job.name,
        data=job.data,
        results=job.results,
        parameters=str(job.parameters),
    )


def job_to_job_core_dto(job: JobDataclass) -> JobCoreDto:
    return JobCoreDto(
        id=job.id,
        executed_by=user_mapper.user_to_user_dto(job.executed_by),
        executed_on=device_mapper.device_to_device_dto(job.executed_on),
        deployment=deployment_mapper.deployment_to_deployment_dto(job.deployment),
        progress=job.progress,
        state=job.state,
        shots=job.shots,
        type=job.type,
        started_at=job.started_at,
        finished_at=job.finished_at,
        name=job.name,
        data=job.data,
        results=[result_mapper.result_to_result_dto(result) for result in job.results],
        parameters=job.parameters,
    )


def job_to_request(job: JobDataclass) -> JobRequestDto:
    return JobRequestDto(
        name=job.name,
        provider_name=job.executed_on.provider.name,
        shots=job.shots,
        parameters=job.parameters,
        token="",
        type=job.type,
        deployment_id=job.deployment.id,
        device_name=job.executed_on.device_name,
    )


def job_to_simple(job: JobDataclass) -> SimpleJobDto:
    return SimpleJobDto(id=job.id, name=job.name, job_state=job.state)
