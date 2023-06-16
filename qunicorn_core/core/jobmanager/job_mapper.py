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
from qunicorn_core.api.api_models import ProviderDto
from qunicorn_core.api.api_models.deployment_dtos import DeploymentDto
from qunicorn_core.api.api_models.device_dtos import DeviceDto
from qunicorn_core.api.api_models.job_dtos import JobResponseDto, JobCoreDto, JobRequestDto
from qunicorn_core.api.api_models.quantum_program_dtos import QuantumProgramDto
from qunicorn_core.api.api_models.user_dtos import UserDto
from qunicorn_core.db.models.job import Job


def request_to_core(job: JobRequestDto):
    user = UserDto(name="default")
    provider = ProviderDto(with_token=True, supported_language = "all", name=job.provider_name)
    device = DeviceDto(provider=provider, url="")
    quantum_program = QuantumProgramDto(quantum_circuit=job.circuit)
    deployment = DeploymentDto(id=None, deployed_by=user, quantum_program=quantum_program, name= "")

    return JobCoreDto(executed_by=user, executed_on=device,
                      deployment=deployment, token=job.token, name=job.name,
                      parameters=job.parameters)


def core_to_response(job: JobCoreDto) -> JobResponseDto:
    return JobResponseDto(id=job.id, executed_by=job.executed_by.name, executed_on=job.executed_on.provider.name, progress=job.progress,
                          state=job.state,
                          started_at=job.started_at, finished_at=job.finished_at, name=job.name, data=job.data, results=job.results,
                          parameters=job.parameter)


def job_core_dto_to_job(job: JobCoreDto) -> Job:
    return Job(id=job.id, executed_by=job.executed_by.id, executed_on=job.executed_on.device_id, deployment_id=job.deployment.id,
               progress=job.progress,
               state=job.state, started_at=job.started_at, finished_at=job.finished_at, name=job.name, data=job.data, results=job.results,
               parameters=job.parameters)


def job_to_job_core_dto(job: Job) -> JobCoreDto:
    return JobCoreDto(id=job.id, executed_by=UserDto(id=job.executed_by), executed_on=DeviceDto(id=job.executed_on),
                      deployment=DeploymentDto(id=job.deployment_id),
                      progress=job.progress, state=job.state, started_at=job.started_at, finished_at=job.finished_at, name=job.name,
                      data=job.data, results=job.results, parameters=job.parameters)
