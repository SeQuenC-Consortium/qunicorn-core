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

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import sqltypes as sql

from ..db import REGISTRY


@REGISTRY.mapped_as_dataclass
class UserDataclass:
    """Dataclass for storing Users

    Attributes:
        id (int): Automatically generated database id. Use the id to fetch this information from the database.
        name (str): Name of the user.
    """

    __tablename__ = "User"

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, init=False)
    name: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
