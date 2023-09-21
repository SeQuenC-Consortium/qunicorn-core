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
from typing import Optional

from qunicorn_core.api.api_models import DeploymentDto, DeploymentRequestDto
from qunicorn_core.api.jwt import abort_unauthorized
from qunicorn_core.core.mapper import deployment_mapper, quantum_program_mapper
from qunicorn_core.db.database_services import deployment_db_service, db_service, job_db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass


def get_all_deployments(user_id: Optional[str] = None) -> list[DeploymentDataclass]:
    """Gets all deployments"""
    return [
        deployment
        for deployment in deployment_db_service.get_all_deployments()
        if deployment.deployed_by is None or deployment.deployed_by == user_id
    ]


def get_deployment_by_id(id: int, user_id: Optional[str] = None) -> DeploymentDataclass:
    """Gets one deployment"""
    deployment = deployment_db_service.get_deployment_by_id(id)
    if deployment.deployed_by is not None and deployment.deployed_by != user_id:
        abort_unauthorized()
    return deployment


def update_deployment(
    deployment_dto: DeploymentRequestDto, deployment_id: int, user_id: Optional[str] = None
) -> DeploymentDto:
    """Updates one deployment"""
    try:
        db_deployment = get_deployment_by_id(deployment_id)
        if db_deployment.deployed_by is not None and db_deployment.deployed_by != user_id:
            abort_unauthorized()
        db_deployment.deployed_at = datetime.now()
        db_deployment.name = deployment_dto.name
        programs = [quantum_program_mapper.request_to_dataclass(qc) for qc in deployment_dto.programs]
        db_deployment.programs = programs
        return db_service.save_database_object(db_deployment)
    except AttributeError:
        db_service.get_session().rollback()
        raise ValueError("Error updating deployment with id: " + str(deployment_id))


def delete_deployment(id: int, user_id: Optional[str] = None) -> DeploymentDto:
    """Remove one deployment by id"""
    db_deployment = deployment_mapper.deployment_to_deployment_dto(deployment_db_service.get_deployment_by_id(id))
    if db_deployment.deployed_by is not None and db_deployment.deployed_by != user_id:
        abort_unauthorized()
    if len(job_db_service.get_jobs_by_deployment_id(db_deployment.id)) > 0:
        raise ValueError("Deployment is in use by a job")
    deployment_db_service.delete(id)
    return db_deployment


def create_deployment(deployment_dto: DeploymentRequestDto, user_id: Optional[str] = None) -> DeploymentDto:
    """Create a deployment and save it in the database"""
    deployment: DeploymentDataclass = deployment_mapper.request_dto_to_deployment(deployment_dto)
    deployment.deployed_by = user_id
    deployment = deployment_db_service.create(deployment)
    return deployment_mapper.deployment_to_deployment_dto(deployment)
