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
from qunicorn_core.celery import CELERY
from qunicorn_core.core.mapper import job_mapper, result_mapper
from qunicorn_core.core.pilotmanager.qiskit_pilot import QiskitPilot
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.provider_name import ProviderName

ASYNCHRONOUS: bool = environ.get("EXECUTE_CELERY_TASK_ASYNCHRONOUS") == "True"


@CELERY.task()
def run_job(job_core_dto_dict: dict):
    """Assign the job to the target pilot which executes the job"""

    job_core_dto: JobCoreDto = yaml.load(job_core_dto_dict["data"], yaml.Loader)

    device = job_core_dto.executed_on
    pilot: QiskitPilot = QiskitPilot("QP")

    if device.provider.name == ProviderName.IBM:
        pilot.execute(job_core_dto)
    else:
        exception: Exception = ValueError("No valid Target specified")
        job_db_service.update_finished_job(job_core_dto.id, result_mapper.get_error_results(exception), JobState.ERROR)
        raise exception


def create_and_run_job(job_request_dto: JobRequestDto, asynchronous: bool = ASYNCHRONOUS) -> SimpleJobDto:
    """First creates a job to let it run afterwards on a pilot"""
    job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
    job: JobDataclass = job_db_service.create_database_job(job_core_dto)
    job_core_dto.id = job.id

    serialized_job_core_dto = yaml.dump(job_core_dto)
    job_core_dto_dict = {"data": serialized_job_core_dto}
    run_job.delay(job_core_dto_dict) if asynchronous else run_job(job_core_dto_dict)
    return SimpleJobDto(id=job_core_dto.id, name=job_core_dto.name, job_state=JobState.RUNNING)


def re_run_job_by_id(job_id: int, token: str) -> SimpleJobDto:
    """Get job from DB, Save it as new job and run it with the new id"""
    job: JobDataclass = job_db_service.get_job(job_id)
    job_request: JobRequestDto = job_mapper.job_to_request(job)
    job_request.token = token
    return create_and_run_job(job_request)


def run_job_by_id(job_id: int, job_exec_dto: JobExecutePythonFileDto, asyn: bool = ASYNCHRONOUS) -> SimpleJobDto:
    """Get uploaded job from DB, and run it on a provider"""
    job: JobDataclass = job_db_service.get_job(job_id)
    job_core_dto: JobCoreDto = job_mapper.job_to_job_core_dto(job)
    job_core_dto.ibm_file_inputs = job_exec_dto.python_file_inputs
    job_core_dto.ibm_file_options = job_exec_dto.python_file_options
    job_core_dto.token = job_exec_dto.token

    serialized_job_core_dto = yaml.dump(job_core_dto)
    job_core_dto_dict = {"data": serialized_job_core_dto}
    run_job.delay(job_core_dto_dict) if asyn else run_job(job_core_dto_dict)

    return SimpleJobDto(id=job_core_dto.id, name=job_core_dto.name, job_state=JobState.RUNNING)


def get_job(job_id: int) -> JobResponseDto:
    """Gets the job from the database service with its id"""
    db_job: JobDataclass = job_db_service.get_job(job_id)
    return job_mapper.job_to_response(db_job)


def delete_job_data_by_id(job_id) -> JobResponseDto:
    """delete job data from db"""
    job = get_job(job_id)
    job_db_service.delete(job_id)
    return job


def get_all_jobs() -> list[SimpleJobDto]:
    """get all jobs from the db"""
    return [job_mapper.job_to_simple(job) for job in job_db_service.get_all()]


def check_registered_pilots():
    """get all registered pilots for computing the schedule"""
    raise NotImplementedError


def schedule_jobs():
    """start the scheduling"""
    raise NotImplementedError


def send_job_to_pilot():
    """send job to pilot for execution after it is scheduled"""
    raise NotImplementedError


def pause_job_by_id(job_id):
    """pause job execution"""
    raise NotImplementedError


def cancel_job_by_id(job_id):
    """cancel job execution"""
    raise NotImplementedError


def get_jobs_by_deployment_id(deployment_id) -> list[JobResponseDto]:
    jobs_by_deployment_id = job_db_service.get_jobs_by_deployment_id(deployment_id)
    return [job_mapper.job_to_response(job) for job in jobs_by_deployment_id]


def delete_jobs_by_deployment_id(deployment_id) -> list[JobResponseDto]:
    jobs = get_jobs_by_deployment_id(deployment_id)
    job_db_service.delete_jobs_by_deployment_id(deployment_id)
    return jobs
