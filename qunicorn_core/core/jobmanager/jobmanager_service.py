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


from qunicorn_core.api.api_models.job_dtos import JobRequestDto, JobCoreDto
from qunicorn_core.celery import CELERY
from qunicorn_core.core.jobmanager import job_mapper
from qunicorn_core.core.pilotmanager.aws_pilot import AWSPilot
from qunicorn_core.core.pilotmanager.qiskit_pilot import QiskitPilot
from qunicorn_core.db.database_services import job_db_service

qiskitpilot = QiskitPilot
awspilot = AWSPilot


@CELERY.task()
def run_job(job_dto_dict: dict):
    """Create a job and assign to the target pilot which executes the job"""

    job_dto: JobCoreDto = JobCoreDto(**job_dto_dict)
    device = job_dto.executed_on
    print(device)
    if device.provider.name == 'IBMQ':
        pilot = qiskitpilot("QP")
        pilot.execute(job_dto)
    else:
        print("No valid target specified")
    return 0

def create_and_run_job(job_request_dto: JobRequestDto) -> JobID:
    job: Job = job_db_service.create_database_job(job_request_dto)
    job_core_dto: JobCoreDto = job_mapper.job_to_job_core_dto(job)
    run_job(vars(job_core_dto))
    return JobID(id=job_core_dto.id, name=job_core_dto, state=JobState.RUNNING)


def get_job(job_id: int) -> JobResponseDto:
    db_job: Job = job_db_service.get_job(job_id)
    return job_mapper.job_to_response(db_job)


def save_job_to_storage():
    """store job for later use"""
    None


def check_registered_pilots():
    """get all registered pilots for computing the schedule"""
    None


def schedule_jobs():
    """start the scheduling"""
    None


def send_job_to_pilot():
    """send job to pilot for execution after it is scheduled"""
    None
