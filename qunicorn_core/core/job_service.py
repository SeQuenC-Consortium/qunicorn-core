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
from typing import Optional

import yaml

from qunicorn_core.api.api_models.job_dtos import (
    JobRequestDto,
    JobCoreDto,
    SimpleJobDto,
    JobResponseDto,
    JobExecutePythonFileDto,
)
from qunicorn_core.api.jwt import abort_if_user_unauthorized
from qunicorn_core.core import job_manager_service
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState

"""
This module contains the service layer for jobs. It is used to create and run jobs.
It calls the job_manager_service to run the jobs with celery.
"""

ASYNCHRONOUS: bool = environ.get("EXECUTE_CELERY_TASK_ASYNCHRONOUS") == "True"


def create_and_run_job(
    job_request_dto: JobRequestDto, is_asynchronous: bool = ASYNCHRONOUS, user_id: Optional[str] = None
) -> SimpleJobDto:
    """First creates a job to let it run afterwards on a pilot"""
    job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
    job_core_dto.executed_by = user_id
    job: JobDataclass = job_db_service.create_database_job(job_core_dto)
    job_core_dto.id = job.id
    run_job_with_celery(job_core_dto, is_asynchronous)
    return SimpleJobDto(id=job_core_dto.id, name=job_core_dto.name, state=JobState.READY)


def run_job_with_celery(job_core_dto: JobCoreDto, is_asynchronous: bool):
    """Serialize the job and run it with celery"""
    serialized_job_core_dto = yaml.dump(job_core_dto)
    job_core_dto_dict = {"data": serialized_job_core_dto}
    if is_asynchronous:
        task = job_manager_service.run_job.delay(job_core_dto_dict)
        job_db_service.update_attribute(job_core_dto.id, task.id, JobDataclass.celery_id)
    else:
        job_manager_service.run_job(job_core_dto_dict)
        job_db_service.update_attribute(job_core_dto.id, "synchronous", JobDataclass.celery_id)


def re_run_job_by_id(job_id: int, token: str, user_id: Optional[str] = None) -> SimpleJobDto:
    """Get job from DB, Save it as new job and run it with the new id"""
    job: JobDataclass = job_db_service.get_job_by_id(job_id)
    abort_if_user_unauthorized(job.executed_by, user_id)
    job_request: JobRequestDto = job_mapper.dataclass_to_request(job)
    job_request.token = token
    return create_and_run_job(job_request)


def run_job_by_id(
    job_id: int, job_exec_dto: JobExecutePythonFileDto, asyn: bool = ASYNCHRONOUS, user_id: Optional[str] = None
) -> SimpleJobDto:
    """EXPERIMENTAL: Get uploaded job from DB, and run it on a provider"""
    job: JobDataclass = job_db_service.get_job_by_id(job_id)
    abort_if_user_unauthorized(job.executed_by, user_id)
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


def delete_job_data_by_id(job_id, user_id: Optional[str]) -> JobResponseDto:
    """delete job data from db"""
    job = get_job_by_id(job_id)
    abort_if_user_unauthorized(job.executed_by, user_id)
    job_db_service.delete(job_id)
    return job


def get_all_jobs(user_id: Optional[str]) -> list[SimpleJobDto]:
    """get all jobs from the db"""
    return [
        job_mapper.dataclass_to_simple(job)
        for job in job_db_service.get_all()
        if job.executed_by is None or job.executed_by == user_id
    ]


def check_registered_pilots():
    """get all registered pilots for computing the schedule"""
    raise NotImplementedError


def schedule_jobs():
    """start the scheduling"""
    raise NotImplementedError


def send_job_to_pilot():
    """send job to pilot for execution after it is scheduled"""
    raise NotImplementedError


def cancel_job_by_id(job_id, token, user_id: Optional[str] = None) -> SimpleJobDto:
    """cancel job execution"""
    job: JobDataclass = job_db_service.get_job_by_id(job_id)
    abort_if_user_unauthorized(job.executed_by, user_id)
    job_core_dto: JobCoreDto = job_mapper.dataclass_to_core(job)
    job_core_dto.token = token
    job_manager_service.cancel_job(job_core_dto)
    return SimpleJobDto(id=job_core_dto.id, name=job_core_dto.name, state=JobState.CANCELED)


def get_jobs_by_deployment_id(deployment_id, user_id: Optional[str]) -> list[JobResponseDto]:
    """get all jobs with the id deployment_id"""
    jobs_by_deployment_id = job_db_service.get_jobs_by_deployment_id(deployment_id)
    for job in jobs_by_deployment_id:
        abort_if_user_unauthorized(job.executed_by, user_id)
    return [job_mapper.dataclass_to_response(job) for job in jobs_by_deployment_id]


def delete_jobs_by_deployment_id(deployment_id, user_id: Optional[str] = None) -> list[JobResponseDto]:
    """delete all jobs with the id deployment_id"""
    jobs = get_jobs_by_deployment_id(deployment_id)
    for job in jobs:
        abort_if_user_unauthorized(job.executed_by, user_id)
    job_db_service.delete_jobs_by_deployment_id(deployment_id)
    return jobs
