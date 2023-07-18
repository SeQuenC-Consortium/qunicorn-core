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
import yaml

from qunicorn_core.api.api_models.job_dtos import (
    JobRequestDto,
    JobCoreDto,
    SimpleJobDto,
    JobResponseDto,
    JobExecutionDto,
)
from qunicorn_core.celery import CELERY
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.core.pilotmanager.qiskit_pilot import QiskitPilot
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.provider_name import ProviderName


@CELERY.task()
def run_job(job_core_dto_dict: dict):
    """Assign the job to the target pilot which executes the job"""

    job_core_dto: JobCoreDto = yaml.load(job_core_dto_dict["data"], yaml.Loader)

    if job_core_dto.executed_on.provider.name == ProviderName.IBM:
        pilot: QiskitPilot = QiskitPilot("QP")
        pilot.execute(job_core_dto)
    else:
        print("WARNING: No valid target specified")
    return 0


def create_and_run_job(job_request_dto: JobRequestDto, asynchronous: bool = False) -> SimpleJobDto:
    """First creates a job to let it run afterwards on a pilot"""
    job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
    job: JobDataclass = job_db_service.create_database_job(job_core_dto)
    job_core_dto.id = job.id

    serialized_job_core_dto = yaml.dump(job_core_dto)
    job_core_dto_dict = {"data": serialized_job_core_dto}
    run_job.delay(job_core_dto_dict) if asynchronous else run_job(job_core_dto_dict)
    return SimpleJobDto(id=job_core_dto.id, name=job_core_dto.name, job_state=JobState.RUNNING)


def run_job_by_id(job_id: int, job_execution_dto: JobExecutionDto, asynchronous: bool = False) -> SimpleJobDto:
    """Get job from DB, Save it as new job and run it with the new id"""
    job: JobDataclass = job_db_service.get_job(job_id)
    job_core_dto: JobCoreDto = job_mapper.job_to_job_core_dto(job)
    job_core_dto.ibm_file_inputs = job_execution_dto.python_file_inputs
    job_core_dto.ibm_file_options = job_execution_dto.python_file_options
    job_core_dto.token = job_execution_dto.token

    serialized_job_core_dto = yaml.dump(job_core_dto)
    job_core_dto_dict = {"data": serialized_job_core_dto}
    run_job.delay(job_core_dto_dict) if asynchronous else run_job(job_core_dto_dict)

    # TODO: run job
    return SimpleJobDto(id=str(job_core_dto.id), name=job_core_dto.name, job_state=JobState.RUNNING)


def get_job(job_id: int) -> JobResponseDto:
    """Gets the job from the database service with its id"""
    db_job: JobDataclass = job_db_service.get_job(job_id)
    return job_mapper.job_to_response(db_job)


def save_job_to_storage():
    """store job for later use"""


def check_registered_pilots():
    """get all registered pilots for computing the schedule"""


def schedule_jobs():
    """start the scheduling"""


def send_job_to_pilot():
    """send job to pilot for execution after it is scheduled"""


def pause_job_by_id(job_id):
    """pause job execution"""
    return "Not implemented yet"


def cancel_job_by_id(job_id):
    """cancel job execution"""
    return "Not implemented yet"


def delete_job_data_by_id(job_id):
    """delete job data"""
    return "Not implemented yet"


def get_all_jobs():
    """get all jobs from the db"""
    return "Not implemented yet"
