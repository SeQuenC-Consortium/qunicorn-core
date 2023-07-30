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
from qiskit.providers import QiskitBackendNotFoundError
from qiskit_ibm_provider import IBMProvider, IBMBackend

from qunicorn_core.api.api_models.device_dtos import DeviceRequest, SimpleDeviceDto, DeviceDto
from qunicorn_core.celery import CELERY
from qunicorn_core.core.mapper import device_mapper
from qunicorn_core.core.pilotmanager.qiskit_pilot import QiskitPilot
from qunicorn_core.db.database_services import db_service, device_db_service
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.static.enums.provider_name import ProviderName


@CELERY.task()
def update_devices(device_request: DeviceRequest):
    """Update all backends for the IBM provider"""
    ibm_provider: IBMProvider = QiskitPilot.get_ibm_provider_and_login(device_request.token)
    devices = ibm_provider.backends()
    all_devices: dict = get_device_dict(devices)

    update_devices_in_db(all_devices=all_devices)

    return all_devices


def update_devices_in_db(all_devices: dict):
    """Preformatting the device data and update/create device data in the database"""
    for device in all_devices["all_devices"]:
        final_device: DeviceDataclass = DeviceDataclass(
            provider_id=device["provider_id"],
            num_qubits=device["num_qubits"],
            device_name=device["name"],
            url=device["url"],
            is_simulator=device["is_simulator"],
            provider=db_service.get_database_object(1, ProviderDataclass),
        )
        db_service.save_device_by_name(final_device)


def get_device_dict(devices: [IBMBackend]) -> dict:
    """Create dict from retrieved list of devices"""
    all_devices: dict = {"all_devices": []}
    for device in devices:
        device_dict = {
            "name": device.name,
            "num_qubits": -1 if device.name.__contains__("stabilizer") else device.num_qubits,
            "url": "",
            "is_simulator": 1 if device.name.__contains__("simulator") else 0,
            "provider_id": 1,
            "provider": None,
        }
        all_devices["all_devices"].append(device_dict)

    return all_devices


def get_all_devices() -> list[SimpleDeviceDto]:
    """Gets all Devices from the DB and maps them"""
    return [device_mapper.device_to_simple_device(device) for device in device_db_service.get_all_devices()]


def get_device(device_id: int) -> DeviceDto:
    """Gets all Devices from the DB and maps them"""
    return device_mapper.device_to_device_dto(device_db_service.get_device(device_id))


def check_if_device_available(device_id: int, token: str) -> dict:
    """Checks if the backend is running"""
    device: DeviceDto = get_device(device_id)
    if device.provider.name == ProviderName.IBM:
        ibm_provider: IBMProvider = QiskitPilot.get_ibm_provider_and_login(token)
        try:
            ibm_provider.get_backend(device.device_name)
        except QiskitBackendNotFoundError:
            return {"backend": "Not Found"}
        finally:
            return {"backend": "Available"}
    else:
        raise ValueError("No valid Provider specified")


def get_device_from_provider(device_id: int, token: str) -> dict:
    """Get the device from the provider and return the configuration as dict"""
    device: DeviceDto = get_device(device_id)

    # TODO add AWS Device and find common calibration data
    if device.provider.name == ProviderName.IBM:
        ibm_provider: IBMProvider = QiskitPilot.get_ibm_provider_and_login(token)
        backend = ibm_provider.get_backend(device.device_name)
        config_dict: dict = vars(backend.configuration())
        config_dict['u_channel_lo'] = None
        config_dict["_qubit_channel_map"] = None
        config_dict['_channel_qubit_map'] = None
        config_dict['_control_channels'] = None
        config_dict['gates'] = None
        return config_dict
    else:
        raise ValueError("No valid Provider specified")
