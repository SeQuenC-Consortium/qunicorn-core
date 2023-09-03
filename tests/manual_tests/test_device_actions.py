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

""""Test class to test the functionality of the job_api"""

import pytest
from qiskit.qasm import QasmError
from qiskit_ibm_provider.accounts import InvalidAccountError
from qiskit_ibm_provider.api.exceptions import RequestsApiError

from qunicorn_core.api.api_models import DeviceRequest
from qunicorn_core.core import devicemanager_service

from tests import test_utils
from tests.conftest import set_up_env
from tests.manual_tests.test_jobmanager_with_ibm import EXPECTED_ID, JOB_FINISHED_PROGRESS, IS_ASYNCHRONOUS
from tests.test_utils import get_object_from_json


#  Write tests for device request and update in database
def test_get_devices_invalid_token():
    """Testing the device request for get request from IBM"""
    app = set_up_env()
    device_request_dto: DeviceRequest = DeviceRequest(provider="IBM", token="abcde")

    with app.app_context():
        with pytest.raises(Exception) as exception:
            devicemanager_service.update_devices(device_request_dto)

    with app.app_context():
        assert RequestsApiError.__name__ in str(exception)


def test_get_devices_empty_token():
    """Testing the device request for get request from IBM"""
    app = set_up_env()
    device_request_dto: DeviceRequest = DeviceRequest(provider="IBM", token="")

    with app.app_context():
        with pytest.raises(Exception) as exception:
            devicemanager_service.update_devices(device_request_dto)

    with app.app_context():
        assert InvalidAccountError.__name__ in str(exception)
