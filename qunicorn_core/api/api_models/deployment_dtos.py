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


"""Module containing all Dtos and their Schemas for tasks in the Deployment API."""
from dataclasses import dataclass
from datetime import datetime

import marshmallow as ma

from .user_dtos import UserDto
from .quantum_program_dtos import QuantumProgramDto
from ..util import MaBaseSchema

__all__ = ["DeploymentDtoSchema", "DeploymentDto"]


@dataclass
class DeploymentDto:
    id: int
    deployed_by: UserDto | None = None
    quantum_program: QuantumProgramDto | None = None
    deployed_at: datetime | None = None
    name: str | None = None


class DeploymentDtoSchema(MaBaseSchema):
    uid = ma.fields.Integer(
        required=False, metadata={"descrption": "UID for the deployment_api"}
    )
    deployed_by = ma.fields.Integer(
        required=False, metadata={"descrption": "Id of the User"}
    )
    quantum_program = ma.fields.Integer(
        required=False, metadata={"descrption": "Id of the quantum program"}
    )
    deployed_at = ma.fields.Date(
        required=False, metadata={"descrption": "Time of Deployment"}
    )
    name = ma.fields.String(
        required=True,
        metadata={"description": "An optional Name for the deployment_api."},
    )
