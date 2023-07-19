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
import datetime

from qunicorn_core.api.api_models.job_dtos import JobCoreDto
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.db.database_services import db_service, device_db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.db.models.user import UserDataclass
from qunicorn_core.static.enums.job_state import JobState


# originally from <https://github.com/buehlefs/flask-template/>


def create_database_job(job_core: JobCoreDto):
    """Creates a database job with the given circuit and saves it in the database"""
    default_user: UserDataclass = db_service.get_database_object(1, UserDataclass)
    deployment: DeploymentDataclass = db_service.get_database_object(job_core.deployment.id, DeploymentDataclass)
    db_job: JobDataclass = job_mapper.job_core_dto_to_job_without_id(job_core)
    db_job.state = JobState.RUNNING
    db_job.progress = 0
    db_job.executed_by = default_user
    db_job.executed_on = device_db_service.get_device_with_name(job_core.executed_on.provider.name)
    db_job.deployment.deployed_by = default_user
    db_job.deployment = deployment
    return db_service.save_database_object(db_job)


def update_attribute(job_id: int, attribute_value, attribute_name):
    """Updates one attribute (attribute_name) of the job with the id job_id"""
    db_service.get_session().query(JobDataclass).filter(JobDataclass.id == job_id).update(
        {attribute_name: attribute_value}
    )
    db_service.get_session().commit()


def update_finished_job(job_id: int, results: list[ResultDataclass], job_state: JobState = JobState.FINISHED):
    """Updates the attributes state and results of the job with the id job_id"""
    job: JobDataclass = get(job_id)
    job.finished_at = datetime.datetime.now()
    job.progress = 100
    job.results = results
    job.state = job_state
    db_service.save_database_object(job)


def get(job_id: int) -> JobDataclass:
    """Gets the job with the job_id from the database"""
    return db_service.get_database_object(job_id, JobDataclass)


def delete(id: int) -> JobDataclass:
    """Removes one job"""

    return db_service.delete_database_object_by_id(JobDataclass, id)


def get_all() -> list[JobDataclass]:
    """Gets all Jobs from the database"""
    return db_service.get_all_database_objects(JobDataclass)
