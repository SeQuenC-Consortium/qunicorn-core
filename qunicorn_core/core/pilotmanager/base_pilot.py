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
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.core.mapper import result_mapper
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType


class Pilot:
    """Base class for Pilots"""

    name: str
    provider_name: ProviderName
    supported_language: AssemblerLanguage

    def __init__(self, name):
        self.name = name


    def run(self, job: JobCoreDto) -> list[ResultDataclass]:
        raise NotImplementedError()

    def is_my_provider(self, provider_name):
        return self.provider_name == provider_name

    def execute(self, job_core_dto: JobCoreDto):
        """Execute a job on an IBM backend using the IBM Pilot"""

        if job_core_dto.type == JobType.RUNNER:
            self.__run(job_core_dto)
        elif job_core_dto.type == JobType.ESTIMATOR:
            self.__estimate(job_core_dto)
        elif job_core_dto.type == JobType.SAMPLER:
            self.__sample(job_core_dto)
        elif job_core_dto.type == JobType.FILE_RUNNER:
            self.__run_file_program(job_core_dto)
        elif job_core_dto.type == JobType.FILE_UPLOAD:
            self.__upload_program(job_core_dto)
        else:
            exception: Exception = ValueError("No valid Job Type specified")
            results = result_mapper.exception_to_error_results(exception)
            job_db_service.update_finished_job(job_core_dto.id, results, JobState.ERROR)
            raise exception

    def __estimate(self, job_core_dto):
        raise NotImplementedError()

    def __sample(self, job_core_dto):
        raise NotImplementedError()

    def __run_file_program(self, job_core_dto):
        raise not NotImplementedError()

    def __upload_program(self, job_core_dto):
        raise not NotImplementedError()
