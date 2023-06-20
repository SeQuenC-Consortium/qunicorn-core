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

from qunicorn_core.api.api_models import DeploymentDto
from qunicorn_core.core.mapper import quantum_program_mapper, user_mapper
from qunicorn_core.db.models.deployment import DeploymentDataclass


def deployment_dto_to_deployment(deployment: DeploymentDto) -> DeploymentDataclass:
    return DeploymentDataclass(
        id=deployment.id,
        deployed_by=user_mapper.user_dto_to_user(deployment.deployed_by),
        quantum_program=quantum_program_mapper.dto_to_quantum_program(deployment.quantum_program),
        deployed_at=deployment.deployed_at,
        name=deployment.name,
    )


def deployment_dto_to_deployment_without_id(deployment: DeploymentDto) -> DeploymentDataclass:
    return DeploymentDataclass(
        deployed_by=user_mapper.user_dto_to_user_without_id(deployment.deployed_by),
        quantum_program=quantum_program_mapper.dto_to_quantum_program_without_id(deployment.quantum_program),
        deployed_at=deployment.deployed_at,
        name=deployment.name,
    )


def deployment_to_deployment_dto(deployment: DeploymentDataclass) -> DeploymentDto:
    return DeploymentDto(
        id=deployment.id,
        deployed_by=user_mapper.user_to_user_dto(deployment.deployed_by),
        quantum_program=quantum_program_mapper.quantum_program_to_dto(deployment.quantum_program),
        deployed_at=deployment.deployed_at,
        name=deployment.name,
    )
