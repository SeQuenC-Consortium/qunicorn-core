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
from qunicorn_core.api.api_models import DeploymentDto, DeploymentRequestDto
from qunicorn_core.core.mapper import deployment_mapper
from qunicorn_core.db.database_services import deployment_db_service, db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass


def get_all_deployments() -> list[DeploymentDto]:
    """Gets all deployments"""
    return deployment_db_service.get_all_deployments()


def get_deployment(id: int) -> DeploymentDto:
    """Gets one deployment"""
    return deployment_db_service.get_deployment(id)


def update_deployment(deployment_dto: DeploymentRequestDto) -> DeploymentDto:
    """Updates one deployment"""
    deployment: DeploymentDataclass = deployment_mapper.request_dto_to_deployment(deployment_dto)
    return db_service.save_database_object(deployment)


def remove_deployment(id: int) -> DeploymentDto:
    """Remove one deployment by id"""
    return deployment_mapper.deployment_to_deployment_dto(deployment_db_service.delete(id))


def create_deployment(deployment_dto: DeploymentRequestDto) -> DeploymentDto:
    """Create a deployment and save it in the database"""

    deployment: DeploymentDataclass = deployment_mapper.request_dto_to_deployment(deployment_dto)
    deployment = deployment_db_service.create(deployment)
    return deployment_mapper.deployment_to_deployment_dto(deployment)
