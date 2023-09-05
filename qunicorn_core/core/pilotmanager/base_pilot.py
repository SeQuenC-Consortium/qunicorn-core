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
from celery.contrib.abortable import AbortableAsyncResult

from qunicorn_core.api.api_models import JobCoreDto
from qunicorn_core.celery import CELERY
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
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

    def cancel(self, job: JobCoreDto):
        print(job)
        if job.state == JobState.CREATED and not JobCoreDto.celery_id == "synchronous":
            print("aborting")
            res = CELERY.AsyncResult(job.celery_id)
            res.revoke()
            job_db_service.update_attribute(job.id, JobState.CANCELED, JobDataclass.state)
            return True
        elif job.state == JobState.RUNNING:
            return self.cancel_provider_specific(job)
        else:
            print("skipping")
            return False

    def run(self, job: JobCoreDto) -> list[ResultDataclass]:
        """Run a job of type RUNNER on a backend using a Pilot"""

        raise NotImplementedError()
    
    def cancel_provider_specific(self, job):
        raise NotImplementedError()

    def execute_provider_specific(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute a job of a provider specific type on a backend using a Pilot"""

        raise NotImplementedError()

    def is_my_provider(self, provider_name):
        return self.provider_name == provider_name
