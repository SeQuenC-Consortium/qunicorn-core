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


"""Module containing all Dtos and their Schemas for tasks in the Users API."""
from dataclasses import dataclass

import marshmallow as ma

from ..flask_api_utils import MaBaseSchema

__all__ = ["UserDtoSchema", "UserDto"]


@dataclass
class UserDto:
    id: int
    name: str | None = None

    @staticmethod
    def get_default_user() -> "UserDto":
        return UserDto(id=1, name="default")


class UserDtoSchema(MaBaseSchema):
    id = ma.fields.Int(required=True, allow_none=False)
    name = ma.fields.String(required=True, allow_none=False)
