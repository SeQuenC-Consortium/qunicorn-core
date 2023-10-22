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
from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import sqltypes as sql

from .db_model import DbModel
from .deployment import DeploymentDataclass
from .device import DeviceDataclass
from .result import ResultDataclass
from ..db import REGISTRY
from ...static.enums.job_state import JobState
from ...static.enums.job_type import JobType


@REGISTRY.mapped_as_dataclass
class JobDataclass(DbModel):
    """Dataclass for storing Jobs

    Attributes:
        name (str, optional): Optional name for a job.
        results (ResultDataclass, optional): List of results for each quantum program that was executed.
        executed_by(str): A user_id associated to the job, user that wants to execute the job.
        executed_on (DeviceDataclass): The device where the job is running on.
        deployment (DeploymentDataclass): The deployment where the program is coming from.
        progress (float): The progress of the job.
        state (str): The state of a job, enum JobState.
        shots (int): The number of shots for the job
        type (JobType): The type of the job.
        started_at (datetime, optional): The moment the job was scheduled. (default: datetime.utcnow)
        id (int): The id of a job.
        provider_specific_id (str, optional): The provider specific id for the job. (Used for canceling)
        celery_id (str, optional): The celery id for the job. (Used for canceling)
        executed_on_id (int, optional): The device_id of the device where the job is running on.
        finished_at (Optional[datetime], optional): The moment the job finished successfully or with an error.
        deployment_id (int): A deployment_id associated with the job.
    """

    # non-default arguments
    name: Mapped[Optional[str]] = mapped_column(sql.String(50))
    results: Mapped[Optional[List[ResultDataclass.__name__]]] = relationship(ResultDataclass.__name__)
    executed_by: Mapped[Optional[str]] = mapped_column(sql.String(100))
    executed_on: Mapped[DeviceDataclass.__name__] = relationship(DeviceDataclass.__name__)
    deployment: Mapped[DeploymentDataclass.__name__] = relationship(DeploymentDataclass.__name__, cascade="save-update")
    progress: Mapped[str] = mapped_column(sql.INTEGER())
    state: Mapped[str] = mapped_column(sql.Enum(JobState))
    shots: Mapped[int] = mapped_column(sql.INTEGER())
    type: Mapped[str] = mapped_column(sql.Enum(JobType))
    started_at: Mapped[datetime] = mapped_column(sql.TIMESTAMP(timezone=True))
    # default arguments
    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, autoincrement=True, default=None)
    provider_specific_id: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
    celery_id: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
    executed_on_id: Mapped[int] = mapped_column(
        ForeignKey(DeviceDataclass.__tablename__ + ".id", ondelete="SET NULL"), default=None, nullable=True
    )
    deployment_id: Mapped[int] = mapped_column(
        ForeignKey(DeploymentDataclass.__tablename__ + ".id", ondelete="SET NULL"), default=None, nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(sql.TIMESTAMP(timezone=True), default=None, nullable=True)
