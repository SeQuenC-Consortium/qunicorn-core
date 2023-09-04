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
from os import environ

import yaml

from qunicorn_core.api.api_models.job_dtos import (
    JobRequestDto,
    JobCoreDto,
    SimpleJobDto,
    JobResponseDto,
    JobExecutePythonFileDto,
)
from qunicorn_core.core import job_manager_service
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState

ASYNCHRONOUS: bool = environ.get("EXECUTE_CELERY_TASK_ASYNCHRONOUS") == "True"


def create_and_run_job(job_request_dto: JobRequestDto, asynchronous: bool = ASYNCHRONOUS) -> SimpleJobDto:
    """First creates a job to let it run afterwards on a pilot"""
    job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
    job: JobDataclass = job_db_service.create_database_job(job_core_dto)
    job_core_dto.id = job.id
    run_job_with_celery(job_core_dto, asynchronous)
    return SimpleJobDto(id=job_core_dto.id, name=job_core_dto.name, state=JobState.RUNNING)


def run_job_with_celery(job_core_dto: JobCoreDto, asynchronous: bool):
    serialized_job_core_dto = yaml.dump(job_core_dto)
    job_core_dto_dict = {"data": serialized_job_core_dto}
    if asynchronous:
        job_manager_service.run_job.delay(job_core_dto_dict)
    else:
        job_manager_service.run_job(job_core_dto_dict)


def re_run_job_by_id(job_id: int, token: str) -> SimpleJobDto:
    """Get job from DB, Save it as new job and run it with the new id"""
    job: JobDataclass = job_db_service.get_job_by_id(job_id)
    job_request: JobRequestDto = job_mapper.dataclass_to_request(job)
    job_request.token = token
    return create_and_run_job(job_request)


def run_job_by_id(job_id: int, job_exec_dto: JobExecutePythonFileDto, asyn: bool = ASYNCHRONOUS) -> SimpleJobDto:
    """Get uploaded job from DB, and run it on a provider"""
    job: JobDataclass = job_db_service.get_job_by_id(job_id)
    job_core_dto: JobCoreDto = job_mapper.dataclass_to_core(job)
    job_core_dto.ibm_file_inputs = job_exec_dto.python_file_inputs
    job_core_dto.ibm_file_options = job_exec_dto.python_file_options
    job_core_dto.token = job_exec_dto.token
    run_job_with_celery(job_core_dto, asyn)
    return SimpleJobDto(id=job_core_dto.id, name=job_core_dto.name, state=JobState.RUNNING)


def get_job_by_id(job_id: int) -> JobResponseDto:
    """Gets the job from the database service with its id"""
    db_job: JobDataclass = job_db_service.get_job_by_id(job_id)
    return job_mapper.dataclass_to_response(db_job)


def delete_job_data_by_id(job_id) -> JobResponseDto:
    """delete job data from db"""
    job = get_job_by_id(job_id)
    job_db_service.delete(job_id)
    return job


def get_all_jobs() -> list[SimpleJobDto]:
    """get all jobs from the db"""
    return [job_mapper.dataclass_to_simple(job) for job in job_db_service.get_all()]


def check_registered_pilots():
    """get all registered pilots for computing the schedule"""
    raise NotImplementedError


def schedule_jobs():
    """start the scheduling"""
    raise NotImplementedError


def send_job_to_pilot():
    """send job to pilot for execution after it is scheduled"""
    raise NotImplementedError


def cancel_job_by_id(job_id):
    """cancel job execution"""
    job: JobDataclass = job_db_service.get_job_by_id(job_id)
    job_request: JobRequestDto = job_mapper.dataclass_to_request(job)
    job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request)
    device = job_core_dto.executed_on

    # TODO: check if job is executed. If not, remove it from the celery queue
    # else:
    if device.provider.name == ProviderName.IBM:
        qiskit_pilot: IBMPilot = IBMPilot("QP")
        qiskit_pilot.cancel(job_core_dto)
    elif job_core_dto.executed_on.provider.name == ProviderName.AWS:
        # cancel aws job not supported yet
        raise NotImplementedError
    


def get_jobs_by_deployment_id(deployment_id) -> list[JobResponseDto]:
    """get all jobs with the id deployment_id"""
    jobs_by_deployment_id = job_db_service.get_jobs_by_deployment_id(deployment_id)
    return [job_mapper.dataclass_to_response(job) for job in jobs_by_deployment_id]


def delete_jobs_by_deployment_id(deployment_id) -> list[JobResponseDto]:
    """delete all jobs with the id deployment_id"""
    jobs = get_jobs_by_deployment_id(deployment_id)
    job_db_service.delete_jobs_by_deployment_id(deployment_id)
    return jobs
