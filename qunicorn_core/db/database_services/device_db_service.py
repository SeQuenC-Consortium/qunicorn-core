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
from qunicorn_core.db.database_services.db_service import session
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.util import logging


def get_device_by_name(device_name: str) -> DeviceDataclass:
    """Returns the default device of the provider with the name provider_name"""
    devices: list[DeviceDataclass] = (
        db_service.get_session().query(DeviceDataclass).filter(DeviceDataclass.name == device_name).all()
    )

    if len(devices) != 1:
        logging.warn(f"There exists multiple or zero devices with the same name {device_name}")

    return devices[0]


def get_all_devices() -> list[DeviceDataclass]:
    """Gets all Devices from the DB"""
    return db_service.get_all_database_objects(DeviceDataclass)


def get_device_by_id(device_id: int) -> DeviceDataclass:
    """Get a device by id"""
    return db_service.get_database_object_by_id(device_id, DeviceDataclass)


def save_device_by_name(device: DeviceDataclass) -> DeviceDataclass:
    """Updates device object in database if it exists and creates new entry if it doesn't exist"""
    device_exists_and_is_updated = (
        session.query(DeviceDataclass)
        .filter(DeviceDataclass.name == device.name)
        .update(
            {"num_qubits": device.num_qubits, "provider_id": device.provider_id, "is_simulator": device.is_simulator}
        )
    )
    if not device_exists_and_is_updated:
        session.add(device)
    session.commit()
    return get_device_by_name(device.name)
