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
from qunicorn_core.api.api_models import JobCoreDto
from qunicorn_core.db.models.result import ResultDataclass
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

    def is_my_provider(self, provider_name):
        return self.provider_name == provider_name
