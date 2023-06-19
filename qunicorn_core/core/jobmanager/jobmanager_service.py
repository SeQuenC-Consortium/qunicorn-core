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


from qunicorn_core.api.api_models.job_dtos import (
    JobRequestDto,
    JobCoreDto,
    JobID,
    JobResponseDto,
)
from qunicorn_core.celery import CELERY
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.core.pilotmanager.aws_pilot import AWSPilot
from qunicorn_core.core.pilotmanager.qiskit_pilot import QiskitPilot
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.provider_name import ProviderName

qiskitpilot = QiskitPilot
awspilot = AWSPilot


@CELERY.task()
def run_job(job_core_dto_dict: dict):
    """Assign the job to the target pilot which executes the job"""

    job_core_dto: JobCoreDto = JobCoreDto(**job_core_dto_dict)
    device = job_core_dto.executed_on
    print(device)
    if device.provider.name == ProviderName.IBM:
        pilot: QiskitPilot = qiskitpilot("QP")
        pilot.execute(job_core_dto)
    else:
        print("No valid target specified")
    return 0


def create_and_run_job(job_request_dto: JobRequestDto) -> JobID:
    """First creates a job to let it run afterwards on a pilot"""
    job: JobDataclass = job_db_service.create_database_job(job_request_dto)
    job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
    job_core_dto.id = job.id
    run_job(vars(job_core_dto))
    return JobID(id=str(job_core_dto.id), name=job_core_dto.name, job_state=JobState.RUNNING)


def run_job_by_id(job_id: int) -> JobID:
    """Get job from DB, Save it as new job and run it with the new id"""
    job: JobDataclass = job_db_service.get_job(job_id)
    job.id = None
    new_job: JobDataclass = job_db_service.create_database_job(job)
    job_core_dto: JobCoreDto = job_mapper.job_to_job_core_dto(new_job)
    # TODO run job
    return JobID(id=str(job_core_dto.id), name=job_core_dto.name, job_state=JobState.RUNNING)


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
