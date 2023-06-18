# Copyright 2023 University of Stuttgart.
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

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import sqltypes as sql

from ..db import REGISTRY

from ...static.enums.provider_name import ProviderName
from ...static.enums.programming_language import ProgrammingLanguage


@REGISTRY.mapped_as_dataclass
class ProviderDataclass:
    """Dataclass for storing Providers

    Attributes:
        id (int): Automatically generated database id. Use the id to fetch this information from the database.
        with_token (bool): If authentication is needed and can be done by passing a token this attribute true.
        supported_language (ProgrammingLanguage): The programming language that this provider supports.
        cloud_service (ProviderName): Name of the cloud service.
    """

    __tablename__ = "Provider"

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, init=False)
    with_token: Mapped[bool] = mapped_column(sql.BOOLEAN, default=None)
    supported_language: Mapped[ProgrammingLanguage] = mapped_column(sql.String(50), default=None)  # TODO: another Table for languages?
    name: Mapped[ProviderName] = mapped_column(sql.String(50), default=None)
