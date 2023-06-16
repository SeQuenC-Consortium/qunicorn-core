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

from qunicorn_core.api.api_models.job_dtos import JobResponseDto, JobCoreDto, JobRequestDto
from qunicorn_core.db.models.job import Job


def request_to_core(job: JobRequestDto):
    return JobCoreDto(
        name=job.name,
        circuit=job.circuit,
        provider=job.provider,
        shots=job.shots,
        parameters=job.parameters,
        token=job.token)


def job_to_response(job: Job) -> JobResponseDto:
    return JobResponseDto(
        id=job.id,
        executed_by=job.executed_by,
        executed_on=job.executed_on,
        progress=job.progress,
        state=job.state,
        started_at=str(job.started_at),
        finished_at=str(job.finished_at),
        name=job.name,
        data=job.data,
        results=job.results,
        parameter=job.parameter)


def job_core_dto_to_job(job: JobCoreDto) -> Job:
    return Job(
        id=job.id,
        xecuted_by=job.executed_by,
        executed_on=job.executed_on,
        deployment_id=job.deployment_id,
        progress=job.progress,
        state=job.state,
        started_at=job.started_at,
        finished_at=job.finished_at,
        name=job.name,
        data=job.data,
        results=job.results,
        parameters=job.parameters)


def job_to_job_core_dto(job: Job) -> JobCoreDto:
    return JobCoreDto(
        id=job.id,
        executed_by=job.executed_by,
        executed_on=job.executed_on,
        deployment_id=job.deployment_id,
        progress=job.progress,
        state=job.state,
        started_at=job.started_at,
        finished_at=job.finished_at,
        name=job.name,
        data=job.data,
        results=job.results,
        parameters=job.parameters)
