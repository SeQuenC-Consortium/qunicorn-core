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

from qunicorn_core.api.api_models import DeploymentDto, DeploymentRequestDto, UserDto
from qunicorn_core.core.mapper import quantum_program_mapper, user_mapper
from qunicorn_core.db.models.deployment import DeploymentDataclass


def deployment_dto_to_deployment(deployment: DeploymentDto) -> DeploymentDataclass:
    return DeploymentDataclass(
        id=deployment.id,
        deployed_by=user_mapper.dto_to_dataclass(deployment.deployed_by),
        programs=[quantum_program_mapper.dto_to_dataclass(qc) for qc in deployment.programs],
        deployed_at=deployment.deployed_at,
        name=deployment.name,
    )


def request_dto_to_deployment(deployment: DeploymentRequestDto) -> DeploymentDataclass:
    return DeploymentDataclass(
        deployed_by=user_mapper.dto_to_dataclass(UserDto.get_default_user()),
        deployed_at=datetime.now(),
        name=deployment.name,
        programs=[quantum_program_mapper.request_to_dataclass(qc) for qc in deployment.programs],
    )


def deployment_to_deployment_dto(deployment: DeploymentDataclass) -> DeploymentDto:
    return DeploymentDto(
        id=deployment.id,
        deployed_by=user_mapper.dataclass_to_dto(deployment.deployed_by),
        programs=[quantum_program_mapper.dataclass_to_dto(qc) for qc in deployment.programs],
        deployed_at=deployment.deployed_at,
        name=deployment.name,
    )
