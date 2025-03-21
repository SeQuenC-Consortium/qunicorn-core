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

import pytest

from qunicorn_core.core import device_service
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.db.models.provider import ProviderDataclass
from tests.conftest import set_up_env


#  Write tests for device request and update in database
def test_get_devices_invalid_token():
    """Testing the device request for get request from IBM"""
    app = set_up_env()
    with app.app_context():
        providers = ProviderDataclass.get_all(where=[ProviderDataclass.name == ProviderName.IBM.value])
        assert len(providers) == 1, "there should be exactly one provider with this name in the database"
        provider_id = providers[0].id

        with pytest.raises(Exception) as exception:
            device_service.update_devices(provider_id=provider_id, token="invalid_token")

    with app.app_context():
        assert "IBMNotAuthorizedError" in str(exception)
