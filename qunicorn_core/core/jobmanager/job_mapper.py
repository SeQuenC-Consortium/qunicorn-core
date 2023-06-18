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
from qunicorn_core.api.api_models.deployment_dtos import DeploymentDto
from qunicorn_core.api.api_models.device_dtos import DeviceDto
from qunicorn_core.api.api_models.job_dtos import JobCoreDto, JobRequestDto, JobResponseDto
from qunicorn_core.api.api_models.quantum_program_dtos import QuantumProgramDto
from qunicorn_core.api.api_models.user_dtos import UserDto
from qunicorn_core.db.models.job import Job
from qunicorn_core.static.enums.job_state import JobState


def request_to_core(job: JobRequestDto):
    """Helper class. When the db objects are saved correctly we do not need it anymore"""
    user = UserDto(id=0, name="default")
    provider = ProviderDto(id=0, with_token=True, supported_language="all", name=job.provider_name)
    device = DeviceDto(id=0, provider=provider, url="")
    quantum_program = QuantumProgramDto(id=0, quantum_circuit=job.circuit)
    deployment = DeploymentDto(id=0, deployed_by=user, quantum_program=quantum_program, name="")

    return JobCoreDto(id=0,
                      executed_by=user,
                      executed_on=device,
                      deployment=deployment,
                      token=job.token,
                      name=job.name,
                      parameters=job.parameters,
                      progress=str(0),
                      state=JobState.READY,
                      shots=job.shots,
                      started_at=datetime.now(),
                      finished_at=datetime.now(),
                      data="",
                      results="")


def core_to_response(job: JobCoreDto) -> JobResponseDto:
    return JobResponseDto(id=job.id,
                          executed_by=job.executed_by.name,
                          executed_on=job.executed_on.provider.name,
                          progress=job.progress,
                          state=job.state,
                          started_at=job.started_at,
                          finished_at=job.finished_at,
                          name=job.name,
                          data=job.data,
                          results=job.results,
                          parameters=job.parameters)


def job_to_response(job: Job) -> JobResponseDto:
    return JobResponseDto(id=job.id,
                          executed_by=str(job.executed_by),
                          executed_on=str(job.executed_on),
                          progress=str(job.progress),
                          state=job.state,
                          started_at=job.started_at,
                          finished_at=job.finished_at,
                          name=job.name,
                          data=job.data,
                          results=job.results,
                          parameters=job.parameters)


def job_core_dto_to_job(job: JobCoreDto) -> Job:
    return Job(id=job.id,
               executed_by=job.executed_by.id,
               executed_on=job.executed_on.id,
               deployment_id=job.deployment.id,
               progress=job.progress,
               state=job.state,
               shots=job.shots,
               started_at=job.started_at,
               finished_at=job.finished_at,
               name=job.name,
               data=job.data,
               results=job.results,
               parameters=job.parameters)


def job_to_job_core_dto(job: Job) -> JobCoreDto:
    return JobCoreDto(id=job.id,
                      executed_by=UserDto(id=job.executed_by),
                      executed_on=DeviceDto(id=job.executed_on),
                      deployment=DeploymentDto(id=job.deployment_id),
                      progress=job.progress,
                      state=job.state,
                      shots=job.shots,
                      started_at=job.started_at,
                      finished_at=job.finished_at,
                      name=job.name,
                      data=job.data,
                      results=job.results,
                      parameters=job.parameters)
