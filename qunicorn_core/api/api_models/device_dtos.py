# Copyright 2023 University of Stuttgart
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


"""Module containing all Dtos and their Schemas for tasks in the Devices API."""
from dataclasses import dataclass

import marshmallow as ma

from .provider_dtos import ProviderDto, ProviderDtoSchema
from ..util import MaBaseSchema

__all__ = ["DeviceDtoSchema", "DeviceIDSchema", "DeviceDto"]


@dataclass
class DeviceDto:
    id: int
    provider: ProviderDto | None = None
    url: str | None = None


class DeviceDtoSchema(MaBaseSchema):
    device_id = ma.fields.Integer(required=True, allow_none=False, metadata={"description": "The unique deviceID."})
    address_url = ma.fields.String(required=True, allow_none=False, metadata={"description": "URL of a device."})
    provider = ProviderDtoSchema()


class DeviceIDSchema(MaBaseSchema):
    device_type = ma.fields.String(required=True, allow_none=False)
    device_id = ma.fields.Integer(required=True, allow_none=False)


class DevicesRequestSchema(MaBaseSchema):
    pass


class DevicesResponseSchema(MaBaseSchema):
    pass
