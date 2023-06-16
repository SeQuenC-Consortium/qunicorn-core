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


"""Module containing all API schemas for tasks in the Devices API."""
from dataclasses import dataclass

import marshmallow as ma

from ..util import MaBaseSchema

__all__ = ["DevicesSchema", "DeviceIDSchema"]


@dataclass
class DEVICES:
    serviceType: str
    description: str
    address: str
    status: str
    name: str
    url: str
    simulator: bool


class DevicesSchema(MaBaseSchema):
    service_types = ma.fields.List(
        cls_or_instance=ma.fields.Str(),
        required=True,
        allow_none=False,
        metadata={"description": "List of available provider_api which can be used with a device."},
    )
    device_id = ma.fields.Integer(required=True, allow_none=False, metadata={"description": "The unique deviceID."})
    name = ma.fields.String(required=True, allow_none=False, metadata={"description": "The name of a device."})
    address_url = ma.fields.String(required=True, allow_none=False, metadata={"description": "URL of a device."})
    status = ma.fields.String(
        required=True,
        allow_none=False,
        metadata={"description": "Availability of a device. [Available], [Not_Available]"},
    )
    description = ma.fields.String(
        required=True,
        allow_none=False,
        metadata={"description": "Short description of a device."},
    )
    simulator = ma.fields.Boolean(
        required=True,
        allow_none=False,
        metadata={"description": "Whether the device is a simulator or a QPU."},
    )


class DeviceIDSchema(MaBaseSchema):
    device_type = ma.fields.String(required=True, allow_none=False)
    device_id = ma.fields.Integer(required=True, allow_none=False)


class DevicesRequestSchema(MaBaseSchema):
    pass


class DevicesResponseSchema(MaBaseSchema):
    pass
