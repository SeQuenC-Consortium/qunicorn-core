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
from typing import List

import marshmallow as ma

from .quantum_program_dtos import QuantumProgramDto
from .user_dtos import UserDto, UserDtoSchema
from ..flask_api_utils import MaBaseSchema

__all__ = ["DeploymentDtoSchema", "DeploymentDto"]


@dataclass
class DeploymentDto:
    id: int
    programs: List[QuantumProgramDto]
    deployed_by: UserDto
    deployed_at: datetime
    name: str


class DeploymentDtoSchema(MaBaseSchema):
    id = ma.fields.Integer(required=False, metadata={"description": "UID for the deployment_api"})
    deployed_by = UserDtoSchema()
    programs = ma.fields.List(ma.fields.Int, required=False, netadata={"description": "Ids of quantum programs"})
    deployed_at = ma.fields.Date(required=False, metadata={"description": "Time of Deployment"})
    name = ma.fields.String(
        required=True,
        metadata={"description": "An optional Name for the deployment_api."},
    )
