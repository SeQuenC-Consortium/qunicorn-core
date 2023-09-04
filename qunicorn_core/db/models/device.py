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
from .provider import ProviderDataclass
from ..db import REGISTRY


@REGISTRY.mapped_as_dataclass
class DeviceDataclass(DbModel):
    """Dataclass for storing CloudDevices of a provider

    Attributes:
        url (str): Rest-endpoint how to connect to the Cloud device
        provider: The provider of the cloud_service with the needed configurations
    """

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, autoincrement=True, default=None)
    provider_id: Mapped[int] = mapped_column(
        ForeignKey(ProviderDataclass.__tablename__ + ".id", ondelete="SET NULL"), default=None
    )
    num_qubits: Mapped[int] = mapped_column(sql.INTEGER, default=-1)
    name: Mapped[str] = mapped_column(sql.String, default="")
    is_simulator: Mapped[bool] = mapped_column(sql.BOOLEAN, default=False)
    is_local: Mapped[bool] = mapped_column(sql.BOOLEAN, default=False)
    provider: Mapped[ProviderDataclass.__name__] = relationship(ProviderDataclass.__name__, default=None)
