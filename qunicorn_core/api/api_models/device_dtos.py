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
from marshmallow.validate import OneOf

from qunicorn_core.api.api_models.provider_dtos import ProviderDto, ProviderDtoSchema
from qunicorn_core.api.flask_api_utils import MaBaseSchema
from qunicorn_core.static.enums.provider_name import ProviderName

__all__ = [
    "DeviceDtoSchema",
    "SimpleDeviceDtoSchema",
    "SimpleDeviceDto",
    "DeviceDto",
    "DeviceRequestDto",
    "DeviceRequestDtoSchema",
]


@dataclass
class DeviceDto:
    id: int
    name: str
    num_qubits: int
    is_simulator: bool
    is_local: bool
    provider: ProviderDto | None = None


@dataclass
class DeviceRequestDto:
    provider_name: ProviderName
    token: str | None = None


class DeviceDtoSchema(MaBaseSchema):
    id = ma.fields.Integer(required=True, allow_none=False, metadata={"description": "The unique deviceID."})
    name = ma.fields.String(required=True, allow_none=False, metadata={"description": "The name of the device."})
    num_qubits = ma.fields.Integer(required=True, allow_none=False)
    is_simulator = ma.fields.Boolean(required=True, allow_none=False)
    is_local = ma.fields.Boolean(required=True, allow_none=False)
    provider = ma.fields.Nested(ProviderDtoSchema())


class DeviceRequestDtoSchema(MaBaseSchema):
    provider_name = ma.fields.String(
        required=True, metadata={"example": ProviderName.IBM.value}, validate=OneOf([p.value for p in ProviderName])
    )
    token = ma.fields.String(required=False, metadata={"example": ""})


@dataclass
class SimpleDeviceDto:
    device_id: int
    device_name: str
    provider_name: str


class SimpleDeviceDtoSchema(MaBaseSchema):
    device_id = ma.fields.Integer(required=True, dump_only=True)
    device_name = ma.fields.String(required=True, dump_only=True)
    provider_name = ma.fields.String(required=True, dump_only=True, validate=OneOf([p.value for p in ProviderName]))


class DevicesResponseSchema(MaBaseSchema):
    pass
