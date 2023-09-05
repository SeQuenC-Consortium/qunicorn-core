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
from qiskit_ibm_provider import IBMProvider

from qunicorn_core.api.api_models.device_dtos import DeviceRequestDto, SimpleDeviceDto, DeviceDto
from qunicorn_core.core import job_manager_service
from qunicorn_core.core.mapper import device_mapper
from qunicorn_core.core.pilotmanager.ibm_pilot import IBMPilot
from qunicorn_core.db.database_services import device_db_service
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.util import logging


def update_devices(device_request: DeviceRequestDto):
    """Update all backends for the provider from device_request"""
    logging.info(f"Update all available devices for {device_request.provider_name} in database.")
    return job_manager_service.update_and_get_devices_from_provider(device_request)


def get_all_devices() -> list[SimpleDeviceDto]:
    """Gets all Devices from the DB and maps them"""
    return [device_mapper.dataclass_to_simple(device) for device in device_db_service.get_all_devices()]


def get_device_by_id(device_id: int) -> DeviceDto:
    """Gets a Device from the DB by its ID and maps it"""
    return device_mapper.dataclass_to_dto(device_db_service.get_device_by_id(device_id))


def check_if_device_available(device_id: int, token: str) -> dict:
    """Checks if the backend is running"""
    device: DeviceDto = get_device_by_id(device_id)
    if device.provider.name == ProviderName.IBM:
        ibm_provider: IBMProvider = IBMPilot.get_ibm_provider_and_login(token)
        try:
            ibm_provider.get_backend(device.name)
            return {"backend": "Available"}
        except QiskitBackendNotFoundError:
            return {"backend": "Not Found"}
    elif device.provider.name == ProviderName.AWS:
        logging.info("AWS local simulator is always available")
        return {"backend": "Available"}
    else:
        raise ValueError("No valid Provider specified")


def get_device_from_provider(device_id: int, token: str) -> dict:
    """Get the device from the provider and return the configuration as dict"""
    device: DeviceDto = get_device_by_id(device_id)

    # TODO add AWS Device and find common calibration data
    if device.provider.name == ProviderName.IBM:
        ibm_provider: IBMProvider = IBMPilot.get_ibm_provider_and_login(token)
        backend = ibm_provider.get_backend(device.name)
        config_dict: dict = vars(backend.configuration())
        config_dict["u_channel_lo"] = None
        config_dict["_qubit_channel_map"] = None
        config_dict["_channel_qubit_map"] = None
        config_dict["_control_channels"] = None
        config_dict["gates"] = None
        return config_dict
    else:
        raise ValueError("No valid Provider specified")
