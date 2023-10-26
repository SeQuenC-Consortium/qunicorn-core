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
from qunicorn_core.core.mapper import quantum_program_mapper
from qunicorn_core.core.mapper.general_mapper import map_from_to
from qunicorn_core.db.models.deployment import DeploymentDataclass


def dto_to_dataclass(deployment: DeploymentDto) -> DeploymentDataclass | None:
    return map_from_to(
        from_object=deployment,
        to_type=DeploymentDataclass,
        fields_mapping={
            "deployed_at": deployment.deployed_at,
            "programs": [quantum_program_mapper.dto_to_dataclass(qc) for qc in deployment.programs],
        },
    )


def request_to_dataclass(deployment: DeploymentRequestDto) -> DeploymentDataclass | None:
    return map_from_to(
        from_object=deployment,
        to_type=DeploymentDataclass,
        fields_mapping={
            "deployed_at": datetime.now(),
            "programs": [quantum_program_mapper.request_to_dataclass(qc) for qc in deployment.programs],
        },
    )


def dataclass_to_dto(deployment: DeploymentDataclass) -> DeploymentDto | None:
    return map_from_to(
        from_object=deployment,
        to_type=DeploymentDto,
        fields_mapping={
            "programs": [quantum_program_mapper.dataclass_to_dto(qc) for qc in deployment.programs],
        },
    )
