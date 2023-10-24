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

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import sqltypes as sql

from .db_model import DbModel
from .quantum_program import QuantumProgramDataclass
from ..db import REGISTRY


@REGISTRY.mapped_as_dataclass
class DeploymentDataclass(DbModel):
    """Dataclass for storing deployments

    Attributes:
        name (str, optional): Optional name for a deployment.
        deployed_at (Date): Date of the creation of a deployment.
        programs (list): A list of quantum programs.
        id (int): The id of a deployment.
        deployed_by (str): The  user_id that deployed this Deployment.
    """

    # non-default arguments
    name: Mapped[Optional[str]] = mapped_column(sql.String(50))
    deployed_at: Mapped[datetime] = mapped_column(sql.TIMESTAMP(timezone=True))
    programs: Mapped[List[QuantumProgramDataclass.__name__]] = relationship(QuantumProgramDataclass.__name__)
    # default arguments
    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, autoincrement=True, default=None)
    deployed_by: Mapped[Optional[str]] = mapped_column(sql.String(100), default=None)
