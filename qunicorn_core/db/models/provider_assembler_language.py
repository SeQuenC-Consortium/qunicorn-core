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


from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import sqltypes as sql

from .db_model import DbModel
from ..db import REGISTRY
from ...static.enums.assembler_languages import AssemblerLanguage


@REGISTRY.mapped_as_dataclass
class ProviderAssemblerLanguageDataclass(DbModel):
    """Dataclass for storing Assembler Languages

    Attributes:
        supported_language (str): The AssemblerLanguage (Enum) which is supported.
        id (int): The ID of the assembler language.
        provider_id (int): The ID of the provider that supports this language.
    """

    # non-default arguments
    supported_language: Mapped[str] = mapped_column(sql.Enum(AssemblerLanguage))
    # default arguments
    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, autoincrement=True, default=None)
    provider_id: Mapped[int] = mapped_column(ForeignKey("Provider.id"), default=None, nullable=True)
