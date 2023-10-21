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
from qunicorn_core.api.api_models import DeviceRequestDto, SimpleDeviceDto
from qunicorn_core.core.mapper import device_mapper
from qunicorn_core.core.pilotmanager.aws_pilot import AWSPilot
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.core.pilotmanager.ibm_pilot import IBMPilot
from qunicorn_core.db.database_services import device_db_service, db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.qunicorn_exception import QunicornError

PILOTS: list[Pilot] = [IBMPilot(), AWSPilot()]

""""This Class is responsible for managing the pilots and their data, all pilots are saved in the PILOTS list"""


def save_default_jobs_and_devices_from_provider():
    """Get all default data from the pilots and save them to the database"""
    for pilot in PILOTS:
        device_list_without_default, default_device = pilot.get_standard_devices()
        saved_device = device_db_service.save_device_by_name(default_device)
        job: JobDataclass = pilot.get_standard_job_with_deployment(saved_device)
        db_service.get_session().add(job)
        db_service.get_session().add_all(device_list_without_default)
        db_service.get_session().commit()


def update_and_get_devices_from_provider(device_request: DeviceRequestDto) -> list[SimpleDeviceDto]:
    """Update the devices from the provider and return all devices from the database"""
    for pilot in PILOTS:
        if pilot.has_same_provider(device_request.provider_name):
            pilot.save_devices_from_provider(device_request)
    return [device_mapper.dataclass_to_simple(device) for device in device_db_service.get_all_devices()]


def check_if_device_available_from_provider(device, token) -> bool:
    for pilot in PILOTS:
        if pilot.has_same_provider(device.provider.name):
            return pilot.is_device_available(device, token)
    return False


def get_device_data_from_provider(device, token) -> dict:
    for pilot in PILOTS:
        if pilot.has_same_provider(device.provider.name):
            return pilot.get_device_data_from_provider(device, token)
    raise QunicornError("No valid Target specified")
