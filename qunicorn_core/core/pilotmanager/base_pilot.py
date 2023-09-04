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

from qunicorn_core.api.api_models import JobCoreDto
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.db.models.user import UserDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName


class Pilot:
    """Base class for Pilots"""

    provider_name: ProviderName
    supported_language: list[AssemblerLanguage]

    def execute(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute a job on a backend using a Pilot"""

        if job_core_dto.type == JobType.RUNNER:
            return self.run(job_core_dto)
        else:
            return self.execute_provider_specific(job_core_dto)

    def run(self, job: JobCoreDto) -> list[ResultDataclass]:
        """Run a job of type RUNNER on a backend using a Pilot"""

        raise NotImplementedError()

    def execute_provider_specific(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute a job of a provider specific type on a backend using a Pilot"""

        raise NotImplementedError()

    def get_standard_provider(self) -> ProviderDataclass:
        """Create the standard ProviderDataclass Object for the pilot and return it"""

        raise NotImplementedError()

    def get_standard_job_with_deployment(self, user: UserDataclass, device: DeviceDataclass) -> JobDataclass:
        """Create the standard ProviderDataclass Object for the pilot and return it"""

    def is_my_provider(self, provider_name):
        return self.provider_name == provider_name

    def get_standard_devices(self) -> (list[DeviceDataclass], DeviceDataclass):
        """Get all devices from the provider"""
        provider_name_lower_case = self.provider_name.lower()

        root_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = "{}{}".format(provider_name_lower_case, "_standard_devices.json")
        path_dir = "{}{}{}{}{}".format(root_dir, os.sep, "pilot_resources", os.sep, file_name)
        with open(path_dir, "r", encoding="utf-8") as f:
            all_devices = json.load(f)

        provider: ProviderDataclass = self.get_standard_provider()
        devices_without_default: list[DeviceDataclass] = []
        default_device: DeviceDataclass
        for device_json in all_devices["all_devices"]:
            device: DeviceDataclass = DeviceDataclass(provider=provider, provider_id=provider.id, **device_json)
            if device.is_local:
                default_device = device
            else:
                devices_without_default.append(device)

        return devices_without_default, default_device
