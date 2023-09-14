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

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import sqltypes as sql
from sqlalchemy.sql.schema import ForeignKey

from .db_model import DbModel
from .job import JobDataclass
from ..db import REGISTRY
from ...static.enums.pilot_state import PilotState
from ...static.enums.programming_language import ProgrammingLanguage


@REGISTRY.mapped_as_dataclass
class PilotDataclass(DbModel):
    """Dataclass for storing Pilots

    Attributes:
        programming_language (ProgrammingLanguage): Programming language that the code should have after translation
        job (int): ID of the job that is executed by the pilot.
        state (PilotState): Represents progress and current state of pilot.
    """

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, autoincrement=True, default=None)
    job_id: Mapped[int] = mapped_column(
        ForeignKey(JobDataclass.__tablename__ + ".id", ondelete="SET NULL"), default=None
    )
    job: Mapped[JobDataclass.__name__] = relationship(JobDataclass.__name__, default=None)

    programming_language: Mapped[[str]] = mapped_column(sql.Enum(ProgrammingLanguage), default=None)
    state: Mapped[PilotState] = mapped_column(sql.String(50), default=None)
