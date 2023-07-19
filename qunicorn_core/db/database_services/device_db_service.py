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

# originally from <https://github.com/buehlefs/flask-template/>

from qunicorn_core.db.database_services import db_service
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.util import logging


def get_device_with_name(provider_name: str) -> DeviceDataclass:
    """Returns the default device of the provider with the name provider_name"""
    devices: list[DeviceDataclass] = (
        db_service.get_session().query(DeviceDataclass).filter(ProviderDataclass.name == provider_name).all()
    )

    if len(devices) != 1:
        logging.warn(f"There exists multiple or zero devices with the same name {provider_name}")

    return devices[0]
