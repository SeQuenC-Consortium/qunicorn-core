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

"""Test class to test the functionality of the job_api"""
from qunicorn_core.api.api_models import ProviderDto, DeviceDto, SimpleDeviceDto
from qunicorn_core.core import provider_service, device_service
from tests.conftest import set_up_env


def test_get_all_provider():
    """Testing if the "get_all"-endpoint of providers works"""
    # GIVEN: Database is initiated correctly
    app = set_up_env()

    # WHEN: get all provider
    with app.app_context():
        all_provider: list[ProviderDto] = provider_service.get_all_providers()
        first_provider: ProviderDto = provider_service.get_provider_by_id(1)

    # THEN: Test if the name and number of providers is correct
    with app.app_context():
        assert len(all_provider) > 0
        assert all_provider[0].name == first_provider.name
        assert type(first_provider) is ProviderDto
        assert type(all_provider[0]) is ProviderDto


def test_get_all_devices():
    """Testing if the "get_all"-endpoint of devices works"""
    # GIVEN: Database is initiated correctly
    app = set_up_env()

    # WHEN: get all devices
    with app.app_context():
        all_devices: list[SimpleDeviceDto] = device_service.get_all_devices()
        first_device: DeviceDto = device_service.get_device_by_id(1)

    # THEN: Test if the name and number of devices is correct
    with app.app_context():
        assert len(all_devices) > 0
        assert all_devices[0].device_name == first_device.name
        assert type(first_device) is DeviceDto
        assert type(all_devices[0]) is SimpleDeviceDto
