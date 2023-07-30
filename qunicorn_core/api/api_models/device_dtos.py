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
from ..flask_api_utils import MaBaseSchema

__all__ = [
    "DeviceDtoSchema",
    "SimpleDeviceDtoSchema",
    "SimpleDeviceDto",
    "DeviceDto",
    "DeviceRequest",
    "DeviceRequestSchema",
]


@dataclass
class DeviceDto:
    id: int
    device_name: str
    num_qubits: int
    is_simulator: bool
    provider: ProviderDto | None = None
    url: str | None = None


@dataclass
class DeviceRequest:
    token: str


class DeviceDtoSchema(MaBaseSchema):
    device_id = ma.fields.Integer(required=True, allow_none=False, metadata={"description": "The unique deviceID."})
    num_qubits = ma.fields.Integer(required=True, allow_none=False)
    is_simulator = ma.fields.Boolean(required=True, allow_none=False)
    address_url = ma.fields.String(required=True, allow_none=False, metadata={"description": "URL of a device."})
    provider = ma.fields.Nested(ProviderDtoSchema())


class DeviceRequestSchema(MaBaseSchema):
    token = ma.fields.String(required=True, example="")


@dataclass
class SimpleDeviceDto:
    device_id: int
    device_name: str
    provider_name: str


class SimpleDeviceDtoSchema(MaBaseSchema):
    device_id = ma.fields.Integer(required=True, dump_only=True)
    device_name = ma.fields.String(required=True, dump_only=True)
    provider_name = ma.fields.String(required=True, dump_only=True)


class DevicesResponseSchema(MaBaseSchema):
    pass
