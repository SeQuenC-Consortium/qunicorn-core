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


@REGISTRY.mapped_as_dataclass
class DeploymentDataclass:
    """Dataclass for storing deployments

    Attributes:
        id (int): Automatically generated database id. Use the id to fetch this information from the database.
        name (str, optional): Optional name for a deployment_api
        deployed_by (str): The  user_id that deployed this Deployment
        deployed_at (Date): Date of the creation of a deployment_api
    """

    __tablename__ = "Deployment"

    id: Mapped[int] = mapped_column(primary_key=True)
    deployed_by: Mapped[int] = mapped_column(ForeignKey("User.id"))
    quantum_program_id: Mapped[int] = mapped_column(ForeignKey("QuantumProgram.id"))
    deployed_at: Mapped[datetime] = mapped_column(sql.TIMESTAMP(timezone=True), default=datetime.utcnow())
    name: Mapped[Optional[str]] = mapped_column(sql.String(50), default=None)
