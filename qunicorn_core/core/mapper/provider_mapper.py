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

from qunicorn_core.api.api_models import ProviderDto
from qunicorn_core.db.models.provider import ProviderDataclass


def provider_dto_to_provider(provider_dto: ProviderDto) -> ProviderDataclass:
    return ProviderDataclass(
        id=provider_dto.id,
        with_token=provider_dto.with_token,
        supported_language=provider_dto.supported_language,
        name=provider_dto.name,
    )


def provider_dto_to_provider_without_id(provider_dto: ProviderDto) -> ProviderDataclass:
    return ProviderDataclass(
        with_token=provider_dto.with_token,
        supported_language=provider_dto.supported_language,
        name=provider_dto.name,
    )


def provider_to_provider_dto(provider: ProviderDataclass) -> ProviderDto:
    return ProviderDto(
        id=provider.id,
        with_token=provider.with_token,
        supported_language=provider.supported_language,
        name=provider.name,
    )
