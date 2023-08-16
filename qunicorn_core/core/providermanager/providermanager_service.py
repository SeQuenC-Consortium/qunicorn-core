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
from qunicorn_core.celery import CELERY
from qunicorn_core.core.pilotmanager.qiskit_pilot import QiskitPilot
from qunicorn_core.db.database_services import db_service, provider_db_service
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.static.enums.provider_name import ProviderName


def get_all_providers() -> list[ProviderDto]:
    """Gets all Devices from the DB and maps them"""
    return [provider_mapper.provider_to_provider_dto(provider) for provider in provider_db_service.get_all_providers()]


def get_provider(provider_id: int) -> ProviderDto:
    """Gets all Devices from the DB and maps them"""
    return provider_mapper.provider_to_provider_dto(provider_db_service.get_provider(provider_id))
