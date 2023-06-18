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

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import sqltypes as sql

from ..db import REGISTRY
from ...static.enums.job_state import JobState


@REGISTRY.mapped_as_dataclass
class Job:
    """Dataclass for storing Jobs
    
    Attributes:
        id (int): Automatically generated database id. Use the id to fetch this information from the database.
        name (str, optional): Optional name for a job
        executed_by (str): A user_id associated to the job, user that wants to execute the job
        deployment_id (int): A deployment_id associated with the job
        state (Optional[str], optional): The state of a job, enum JobState
        started_at (datetime, optional): The moment the job was scheduled.
            (default :py:func:`~datetime.datetime.utcnow`)
        finished_at (Optional[datetime], optional): The moment the job finished successfully or with an error.
        data (Union[dict, list, str, float, int, bool, None], optional): Mutable JSON-like store for additional
            lightweight task data. Default value is empty dict.
        results (str, optional): The output data (files) of the job
        parameters (str, optional): The parameters for the Job. Job parameters should already be prepared and error
            checked before starting the task.
    """

    __tablename__ = "Job"

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, init=False)
    executed_by: Mapped[int] = mapped_column(ForeignKey("User.id"), default=None, nullable=True)
    executed_on: Mapped[int] = mapped_column(ForeignKey("CloudDevice.id"), default=None, nullable=True)
    deployment_id: Mapped[int] = mapped_column(ForeignKey("Deployment.id"), default=None, nullable=True)
    progress: Mapped[str] = mapped_column(sql.INTEGER(), default=None)
    state: Mapped[str] = mapped_column(sql.Enum(JobState), default=None)
    shots: Mapped[int] = mapped_column(sql.INTEGER(), default=4000)
    started_at: Mapped[datetime] = mapped_column(sql.TIMESTAMP(timezone=True), default=datetime.utcnow())
    finished_at: Mapped[Optional[datetime]] = mapped_column(sql.TIMESTAMP(timezone=True), default=None, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
    data: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
    results: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
    parameters: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
