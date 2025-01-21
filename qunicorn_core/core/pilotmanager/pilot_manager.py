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
import uuid
from http import HTTPStatus
from typing import Optional, Union

import requests
from flask import current_app

from qunicorn_core.api.api_models import DeviceDto
from qunicorn_core.core.pilotmanager.aws_pilot import AWSPilot
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.core.pilotmanager.ibm_pilot import IBMPilot
from qunicorn_core.core.pilotmanager.qmware_pilot import QMwarePilot
from qunicorn_core.core.pilotmanager.rigetti_pilot import RigettiPilot
from qunicorn_core.core.pilotmanager.ionq_pilot import IonQPilot
from qunicorn_core.db.db import DB
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.static.qunicorn_exception import QunicornError

PILOTS: list[Pilot] = [IBMPilot(), AWSPilot(), RigettiPilot(), QMwarePilot(), IonQPilot()]
provider_name_map = {"IBM": "ibmq"}  # "<Qunicorn Provider Name>: <QPROV Provider Name>"

""""This Class is responsible for managing the pilots and their data, all pilots are saved in the PILOTS list"""


def save_default_jobs_and_devices_from_provider(include_default_jobs=True):
    """Get all default data from the pilots and save them to the database"""
    for pilot in PILOTS:
        _, default_device = pilot.get_standard_devices()
        if include_default_jobs:
            job: JobDataclass = pilot.get_standard_job_with_deployment(default_device)
            job.save()
    DB.session.commit()


def update_devices_from_provider(provider_id: int, token: Optional[str]):
    """Update the devices from the provider and return all devices from the database"""
    provider: ProviderDataclass = ProviderDataclass.get_by_id_or_404(provider_id)
    pilot: Pilot = get_matching_pilot(provider.name)
    pilot.save_devices_from_provider(token)

    updated_provider = ProviderDataclass.get_by_id_or_404(provider_id)
    qprov_provider_name = provider_name_map[updated_provider.name]
    qprov_root_url = current_app.config.get("QPROV_URL")

    if qprov_root_url is None:
        current_app.logger.info("QPROV_URL not set, skipping QPROV update")
        return

    response = requests.get(f"{qprov_root_url}/providers")
    response.raise_for_status()
    qprov_providers = response.json()["_embedded"]["providerDtoes"]

    for qprov_provider in qprov_providers:
        if qprov_provider["name"] == qprov_provider_name:
            qprov_id = qprov_provider["id"]
            provider.qprov_id = uuid.UUID(qprov_id)

            response = requests.get(f"{qprov_root_url}/providers/{qprov_id}/qpus")
            response.raise_for_status()
            qprov_qpus = response.json()["_embedded"]["qpuDtoes"]
            qpu_name_id_map = {}

            for qpu in qprov_qpus:
                qpu_name_id_map[qpu["name"]] = qpu["id"]

            for device in updated_provider.devices:
                if device.name in qpu_name_id_map:
                    device.qprov_id = uuid.UUID(qpu_name_id_map[device.name])

            provider.save(commit=True)


def check_if_device_available_from_provider(device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> bool:
    """Checks if a device is currently available at the cloud provider"""
    provider_name = device.provider.name if device.provider else None
    if provider_name is None:
        raise QunicornError(f"Device '{device.name}' ({device.id}) has no provider!", HTTPStatus.INTERNAL_SERVER_ERROR)
    pilot: Pilot = get_matching_pilot(provider_name)
    return pilot.is_device_available(device, token)


def get_device_data_from_provider(device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> dict:
    """Gets the data of a single device by requesting it from the cloud provider"""
    pilot: Pilot = get_matching_pilot(device.provider.name)
    return pilot.get_device_data_from_provider(device, token)


def get_matching_pilot(provider_name: str) -> Pilot:
    """Get the pilot that matches the provider name, if no pilot matches raise an error"""
    for pilot in PILOTS:
        if pilot.has_same_provider(provider_name):
            return pilot
    raise QunicornError(f"No valid Target specified to get device data: {provider_name}")
