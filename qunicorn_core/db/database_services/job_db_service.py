# Copyright 2021 QHAna plugin runner contributors.
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

# originally from <https://github.com/buehlefs/flask-template/>

from datetime import datetime

from qunicorn_core.api.api_models.job_dtos import JobRequestDto
from qunicorn_core.db.database_services import db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.static.enums.job_state import JobState


def create_database_job(job: JobRequestDto):
    """Creates a database job with the given circuit and saves it in the database"""
    db_quantum_program = QuantumProgramDataclass(quantum_circuit = job.circuit)
    db_deployment = DeploymentDataclass(quantum_program = db_quantum_program, name = "new deployment")
    db_job: JobDataclass = JobDataclass(
        data=job.circuit, state=JobState.READY, progress=0, started_at=datetime.now(), shots = job.shots, deployment = db_deployment
    )
    return db_service.save_database_object(db_job)


def update_attribute(job_id: int, job_state: JobState, attribute_name):
    """Updates one attribute (attribute_name) of the job with the id job_id"""
    db_service.get_session().query(JobDataclass).filter(JobDataclass.id == job_id).update(
        {attribute_name: job_state}
    )
    db_service.get_session().commit()


def update_result_and_state(job_id: int, job_state: JobState, results: str):
    """Updates the attributes state and results of the job with the id job_id"""
    db_service.get_session().query(JobDataclass).filter(JobDataclass.id == job_id).update(
        {JobDataclass.state: job_state, JobDataclass.results: results}
    )
    db_service.get_session().commit()


def get_job(job_id: int) -> JobDataclass:
    """Gets the job with the job_id from the database"""
    return db_service.get_database_object(job_id, JobDataclass)
