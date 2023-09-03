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

from qunicorn_core.api.api_models import DeviceDto
from qunicorn_core.api.api_models.device_dtos import SimpleDeviceDto
from qunicorn_core.core.mapper import provider_mapper
from qunicorn_core.core.mapper.general_mapper import map_from_to
from qunicorn_core.db.models.device import DeviceDataclass


def dto_to_dataclass(device: DeviceDto) -> DeviceDataclass:
    return map_from_to(
        from_object=device,
        to_type=DeviceDataclass,
        fields_mapping={
            "provider": provider_mapper.dto_to_dataclass(device.provider),
        },
    )


def dataclass_to_dto(device: DeviceDataclass) -> DeviceDto:
    return map_from_to(
        from_object=device,
        to_type=DeviceDto,
        fields_mapping={
            "provider": provider_mapper.dataclass_to_dto(device.provider),
        },
    )


def dataclass_to_simple(device: DeviceDataclass) -> SimpleDeviceDto:
    return map_from_to(device, SimpleDeviceDto)
