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
import json
import os
from typing import Optional

from celery.states import PENDING

from qunicorn_core.api.api_models import JobCoreDto, DeviceRequestDto, DeviceDto
from qunicorn_core.celery import CELERY
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.qunicorn_exception import QunicornError


class Pilot:
    """Base class for Pilots"""

    provider_name: ProviderName
    supported_languages: list[AssemblerLanguage]

    def run(self, job: JobCoreDto) -> list[ResultDataclass]:
        """Run a job of type RUNNER on a backend using a Pilot"""
        raise NotImplementedError()

    def execute_provider_specific(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute a job of a provider specific type on a backend using a Pilot"""
        raise NotImplementedError()

    def get_standard_provider(self) -> ProviderDataclass:
        """Create the standard ProviderDataclass Object for the pilot and return it"""
        raise NotImplementedError()

    def get_standard_job_with_deployment(self, device: DeviceDataclass, user_id: Optional[str] = None) -> JobDataclass:
        """Create the standard ProviderDataclass Object for the pilot and return it"""
        raise NotImplementedError()

    def save_devices_from_provider(self, device_request: DeviceRequestDto):
        """Create the standard ProviderDataclass Object for the pilot and return it"""
        raise NotImplementedError()

    def is_device_available(self, device: DeviceDto, token: str) -> bool:
        """Check if a device is available for a user"""
        raise NotImplementedError()

    def get_device_data_from_provider(self, device: DeviceDto, token: str) -> dict:
        """Get device data for a specific device from the provider"""
        raise NotImplementedError()

    def execute(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute a job on a backend using a Pilot"""

        if job_core_dto.type == JobType.RUNNER:
            return self.run(job_core_dto)
        else:
            return self.execute_provider_specific(job_core_dto)

    def cancel(self, job: JobCoreDto):
        """Cancel the execution of a job, locally or if that is not possible at the backend"""
        if job.state == JobState.READY and not JobCoreDto.celery_id == "synchronous":
            res = CELERY.AsyncResult(job.celery_id)
            if res.status == PENDING:
                res.revoke()
                job_db_service.update_attribute(job.id, JobState.CANCELED, JobDataclass.state)
        elif job.state == JobState.RUNNING:
            self.cancel_provider_specific(job)
        else:
            raise QunicornError(f"Job is in invalid state for canceling: {job.state}")

    def cancel_provider_specific(self, job):
        """Cancel execution of a job at the corresponding backend"""
        raise NotImplementedError()

    def has_same_provider(self, provider_name: ProviderName) -> bool:
        """Check if the provider name is the same as the pilot provider name"""
        return self.provider_name == provider_name

    def get_standard_devices(self) -> (list[DeviceDataclass], DeviceDataclass):
        """Get all devices from the provider"""

        root_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = "{}{}".format(self.provider_name.lower(), "_standard_devices.json")
        path_dir = "{}{}{}{}{}".format(root_dir, os.sep, "pilot_resources", os.sep, file_name)
        with open(path_dir, "r", encoding="utf-8") as f:
            all_devices = json.load(f)

        provider: ProviderDataclass = self.get_standard_provider()
        devices_without_default: list[DeviceDataclass] = []
        default_device: DeviceDataclass | None = None
        for device_json in all_devices["all_devices"]:
            device: DeviceDataclass = DeviceDataclass(provider=provider, provider_id=provider.id, **device_json)
            if device.is_local:
                default_device = device
            else:
                devices_without_default.append(device)

        if default_device is None:
            raise QunicornError("No default device found for provider {}".format(self.provider_name))

        return devices_without_default, default_device

    @staticmethod
    def qubits_decimal_to_hex(qubits_in_binary: dict, job_id: int) -> dict:
        """To make sure that the qubits in the counts or probabilities are in hex format and not in decimal format"""

        try:
            return dict([(hex(k), v) for k, v in qubits_in_binary.items()])
        except Exception:
            raise job_db_service.return_exception_and_update_job(
                job_id, QunicornError("Could not convert decimal-results to hex")
            )

    @staticmethod
    def qubit_binary_to_hex(qubits_in_binary: dict, job_id: int) -> dict:
        """To make sure that the qubits in the counts or probabilities are in hex format and not in binary format"""

        try:
            return dict([(hex(int(k, 2)), v) for k, v in qubits_in_binary.items()])
        except Exception:
            raise job_db_service.return_exception_and_update_job(
                job_id, QunicornError("Could not convert binary-results to hex")
            )
