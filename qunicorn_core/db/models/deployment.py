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
from .quantum_program import QuantumProgramDataclass
from .user import UserDataclass
from ..db import REGISTRY


@REGISTRY.mapped_as_dataclass
class DeploymentDataclass(DbModel):
    """Dataclass for storing deployments

    Attributes:
        name (str, optional): Optional name for a deployment_api
        deployed_by (str): The  user_id that deployed this Deployment
        programs (list): A list of quantum programs
        deployed_at (Date): Date of the creation of a deployment_api
    """

    deployed_by_id: Mapped[int] = mapped_column(ForeignKey(UserDataclass.__tablename__ + ".id"), default=None, nullable=True)
    deployed_by: Mapped[UserDataclass.__name__] = relationship(UserDataclass.__name__, default=None)
    programs: Mapped[List[QuantumProgramDataclass.__name__]] = relationship(
        QuantumProgramDataclass.__name__,
        default=None,
    )
    deployed_at: Mapped[datetime] = mapped_column(sql.TIMESTAMP(timezone=True), default=datetime.utcnow())
    name: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
