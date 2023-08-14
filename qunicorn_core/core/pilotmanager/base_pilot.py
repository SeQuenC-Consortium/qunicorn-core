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
from qunicorn_core.core.mapper import result_mapper
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType


class Pilot:
    """Base class for Pilots"""

    def __init__(self, name=None):
        self.name = name

    LANGUAGE: AssemblerLanguage = None

    def execute(self, job_dto: JobCoreDto):
        raise ValueError("No valid Job Type specified")

    def run(self, job_dto: JobCoreDto, circuit):
        raise ValueError("No valid Job Type specified")

    def estimate(self, job_dto: JobCoreDto, circuit):
        raise ValueError("No valid Job Type specified")

    def sample(self, job_dto: JobCoreDto, circuit):
        raise ValueError("No valid Job Type specified")
