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
from datetime import datetime

from qunicorn_core.api.api_models import DeploymentDto, DeploymentRequestDto
from qunicorn_core.core.mapper import deployment_mapper, quantum_program_mapper
from qunicorn_core.db.database_services import deployment_db_service, db_service, job_db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.user import UserDataclass


def get_all_deployments() -> list[DeploymentDto]:
    """Gets all deployments"""
    return deployment_db_service.get_all_deployments()


def get_deployment(id: int) -> DeploymentDataclass:
    """Gets one deployment"""
    return deployment_db_service.get_deployment(id)


def update_deployment(deployment_dto: DeploymentRequestDto, deployment_id: int) -> DeploymentDto:
    """Updates one deployment"""
    try:
        db_deployment = get_deployment(deployment_id)
        db_deployment.deployed_by = db_service.get_database_object(0, UserDataclass)
        db_deployment.deployed_at = datetime.now()
        db_deployment.name = deployment_dto.name
        programs = [quantum_program_mapper.request_to_quantum_program(qc) for qc in deployment_dto.programs]
        db_deployment.programs = programs
        return db_service.save_database_object(db_deployment)
    except AttributeError:
        db_service.get_session().rollback()
        raise ValueError("Error updating deployment with id: " + str(deployment_id))


def delete_deployment(id: int) -> DeploymentDto:
    """Remove one deployment by id"""
    db_deployment = deployment_mapper.deployment_to_deployment_dto(deployment_db_service.get_deployment(id))
    if len(job_db_service.get_jobs_by_deployment_id(db_deployment.id)) > 0:
        raise ValueError("Deployment is in use by a job")
    deployment_db_service.delete(id)
    return db_deployment


def create_deployment(deployment_dto: DeploymentRequestDto) -> DeploymentDto:
    """Create a deployment and save it in the database"""

    deployment: DeploymentDataclass = deployment_mapper.request_dto_to_deployment(deployment_dto)
    deployment = deployment_db_service.create(deployment)
    return deployment_mapper.deployment_to_deployment_dto(deployment)
