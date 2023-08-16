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

from qunicorn_core.core.mapper import provider_mapper
from qunicorn_core.api.api_models.provider_dtos import ProviderDto
from qunicorn_core.db.database_services import provider_db_service


def get_all_providers() -> list[ProviderDto]:
    """Gets all Providers from the DB and maps them"""
    return [provider_mapper.dataclass_to_dto(provider) for provider in provider_db_service.get_all_providers()]


def get_provider_by_id(provider_id: int) -> ProviderDto:
    """Gets a Provider from the DB by its ID and maps it"""
    return provider_mapper.dataclass_to_dto(provider_db_service.get_provider_by_id(provider_id))
