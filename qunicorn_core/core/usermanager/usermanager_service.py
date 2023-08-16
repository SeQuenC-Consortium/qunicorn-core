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

from qunicorn_core.core.mapper import user_mapper
from qunicorn_core.api.api_models.user_dtos import UserDto
from qunicorn_core.db.database_services import user_db_service


def get_all_users() -> list[UserDto]:
    """Gets all Devices from the DB and maps them"""
    return [user_mapper.user_to_user_dto(user) for user in user_db_service.get_all_users()]


def get_user(user_id: int) -> UserDto:
    """Gets all Devices from the DB and maps them"""
    return user_mapper.user_to_user_dto(user_db_service.get_user(user_id))
