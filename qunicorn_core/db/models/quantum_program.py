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

from typing import Optional, Sequence, List, Union

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import sqltypes as sql
from sqlalchemy.sql import sqltypes as sql
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import ForeignKey
from .deployment import DeploymentDataclass

from ..db import MODEL, REGISTRY

from datetime import datetime

from ..enums.job_state import JobState
from ..enums.programming_language import ProgrammingLanguage


@REGISTRY.mapped_as_dataclass
class QuantumProgramDataclass:
    """Dataclass for storing QuantumPrograms
    
    Attributes:
        id (int): automatically generated database id. Use the id to fetch this information from the database.
        quantum_circuit (str): quantum code that needs to be executed.
    """

    __tablename__ = "QuantumProgram"

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, init=False)
    quantum_circuit: mapped_column(sql.BLOB, default=None)
