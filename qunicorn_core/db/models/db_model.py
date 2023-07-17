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
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy.sql import sqltypes as sql


class DbModel:
    """Dataclass for database model to create a table name and the id column

    Attributes:
        id (int): Automatically generated id of the database entity
    """

    @declared_attr
    def __tablename__(self):
        return self.__name__.replace("Dataclass", "")

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, autoincrement=True, default=None)
