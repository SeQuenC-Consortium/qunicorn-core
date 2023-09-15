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
from qunicorn_core.api.api_models.pilot_assembler_language_dtos import PilotAssemblerLanguageListDto
from qunicorn_core.core.mapper.general_mapper import map_from_to
from qunicorn_core.db.models.pilot_assembler_language_list import PilotAssemblerLanguageListDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage


def dto_to_dataclass(provider_dto: ProviderDto) -> ProviderDataclass:
    return map_from_to(provider_dto, ProviderDataclass,
                       {"supported_languages": [PilotAssemblerLanguageListDataclass(0, AssemblerLanguage.QISKIT)]})


def dataclass_to_dto(provider: ProviderDataclass) -> ProviderDto:
    return map_from_to(provider, ProviderDto, fields_mapping={
        "supported_languages": PilotAssemblerLanguageListDto(0, AssemblerLanguage.QISKIT)})
