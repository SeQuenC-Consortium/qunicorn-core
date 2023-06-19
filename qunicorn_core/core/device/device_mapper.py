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
from qunicorn_core.core.provider import provider_mapper
from qunicorn_core.db.models.device import DeviceDataclass


def device_dto_to_device(device: DeviceDto) -> DeviceDataclass:
    return DeviceDataclass(
        provider=provider_mapper.provider_dto_to_provider(device.provider), url=device.url
    )


def device_to_device_dto(device: DeviceDataclass) -> DeviceDto:
    return DeviceDto(
        provider=provider_mapper.provider_to_provider_dto(device.provider), url=device.url
    )
