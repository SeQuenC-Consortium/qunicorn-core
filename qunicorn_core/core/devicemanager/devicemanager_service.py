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
from qiskit_ibm_provider import IBMProvider, IBMBackend

from qunicorn_core.api.api_models.device_dtos import DeviceRequest
from qunicorn_core.celery import CELERY
from qunicorn_core.core.pilotmanager.qiskit_pilot import QiskitPilot
from qunicorn_core.db.database_services import db_service
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.provider import ProviderDataclass


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
