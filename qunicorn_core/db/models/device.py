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

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import sqltypes as sql
from sqlalchemy.sql.schema import ForeignKey

from ..db import REGISTRY


@REGISTRY.mapped_as_dataclass
class DeviceDataclass:
    """Dataclass for storing CloudDevices of a provider

    Attributes:
        id (int): Automatically generated database id. Use the id to fetch this information from the database.
        rest_endpoint (str): Rest-endpoint how to connect to the Cloud device
        provider: The provider of the cloud_service with the needed configurations
    """

    __tablename__ = "CloudDevice"

    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, init=False)
    provider: Mapped[int] = mapped_column(ForeignKey("Provider.id"))
    rest_endpoint: Mapped[str] = mapped_column(sql.String(50), default=None)
