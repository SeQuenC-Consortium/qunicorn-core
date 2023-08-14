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


class Pilot:
    """Base class for Pilots"""

    LANGUAGE: AssemblerLanguage = None

    def __init__(self, job_core_dto: JobCoreDto):
        self.provider_name = job_core_dto.executed_on.provider.name
        self.device_name = job_core_dto.executed_on.device_name

    def execute(self, job_dto: JobCoreDto):
        raise ValueError("No valid Job Type specified")

    def run(self, circuit, shots: int) -> list[ResultDataclass]:
        raise ValueError("No valid Job Type specified")

    def estimate(self, circuit) -> list[ResultDataclass]:
        raise ValueError("No valid Job Type specified")

    def sample(self, circuit) -> list[ResultDataclass]:
        raise ValueError("No valid Job Type specified")
