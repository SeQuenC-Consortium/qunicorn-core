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


"""Module containing all Dtos and their Schemas  for tasks in the Services API."""
from dataclasses import dataclass
from ..flask_api_utils import MaBaseSchema
import marshmallow as ma

__all__ = ["ProviderAssemblerLanguageDto", "ProviderAssemblerLanguageDtoSchema"]

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage


@dataclass
class ProviderAssemblerLanguageDto:
    id: int
    provider_id: int
    supported_language: AssemblerLanguage


class ProviderAssemblerLanguageDtoSchema(MaBaseSchema):
    id = ma.fields.Integer(required=True, allow_none=False)
    provider_id = ma.fields.String(required=True, allow_none=False)
    name = ma.fields.Enum(required=True, allow_none=False, enum=AssemblerLanguage)
