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
from qunicorn_core.db.models.device import DeviceDataclass


def device_dto_to_device(device: DeviceDto) -> DeviceDataclass:
    return DeviceDataclass(
        id=device.id,
        num_qubits=device.num_qubits,
        is_simulator=device.is_simulator,
        provider=provider_mapper.dto_to_dataclass(device.provider),
        device_name=device.device_name,
        url=device.url,
    )


def device_dto_to_device_without_id(device: DeviceDto) -> DeviceDataclass:
    return DeviceDataclass(
        num_qubits=device.num_qubits,
        is_simulator=device.is_simulator,
        provider=provider_mapper.dto_to_dataclass(device.provider),
        device_name=device.device_name,
        url=device.url,
    )


def device_to_device_dto(device: DeviceDataclass) -> DeviceDto:
    return DeviceDto(
        id=device.id,
        num_qubits=device.num_qubits,
        is_simulator=device.is_simulator,
        provider=provider_mapper.dataclass_to_dto(device.provider),
        device_name=device.device_name,
        url=device.url,
    )


def device_to_simple_device(device: DeviceDataclass) -> SimpleDeviceDto:
    return SimpleDeviceDto(
        device_id=device.id,
        device_name=device.device_name,
        provider_name=device.provider.name,
    )
