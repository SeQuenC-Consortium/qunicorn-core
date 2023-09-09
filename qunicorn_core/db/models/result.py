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
from ...static.enums.result_type import ResultType


@REGISTRY.mapped_as_dataclass
class ResultDataclass(DbModel):
    """Dataclass for storing results of a job

    Attributes: TODO
        result_dict (dict): The results of the job, in the given result_type
        job_id (int): The  job_id that was executed
        circuit (str): The circuit which was executed by the job
        meta_data (dict): Some other data that was given by ibm
        result_type (Enum): Result type depending on the Job_Type of the job
    """

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, autoincrement=True, default=None)
    result_dict: Mapped[dict] = mapped_column(sql.JSON, default=None, nullable=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("Job.id", ondelete="CASCADE"), default=None, nullable=True)
    circuit: Mapped[str] = mapped_column(sql.String(500), default=None, nullable=True)
    meta_data: Mapped[dict] = mapped_column(sql.JSON, default=None, nullable=True)
    result_type: Mapped[str] = mapped_column(sql.Enum(ResultType), default=ResultType.COUNTS)
