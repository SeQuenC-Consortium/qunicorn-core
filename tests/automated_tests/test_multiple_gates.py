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

""""Test class to test the functionality of the job_api"""

from qunicorn_core.api.api_models import DeploymentRequestDto, DeploymentDto, JobRequestDto, SimpleJobDto
from qunicorn_core.core import deployment_service, job_service
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils
from tests.conftest import set_up_env
from tests.test_utils import IS_ASYNCHRONOUS, get_object_from_json


def test_multiple_gates_aws():
    create_and_test_multiple_gates_deployment(ProviderName.AWS)


def test_multiple_gates_ibm():
    create_and_test_multiple_gates_deployment(ProviderName.IBM)


def create_and_test_multiple_gates_deployment(provider_name: ProviderName):
    """
    Tests the create and run job method for synchronous execution of an estimator
    Tested Gates: X, Y, Z, H, CX, CXX, S, T
    """
    # GIVEN: Database Setup & job_request_dto created
    app = set_up_env()
    job_request_dto: JobRequestDto = test_utils.get_test_job(provider_name)

    # WHEN: create_and_run executed synchronous
    with app.app_context():
        deployment_path: str = "deployment_request_dto_multiple_gates_test_data.json"
        deployment_request: DeploymentRequestDto = DeploymentRequestDto.from_dict(get_object_from_json(deployment_path))
        deployment: DeploymentDto = deployment_service.create_deployment(deployment_request)
        job_request_dto.deployment_id = deployment.id
        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        test_utils.check_simple_job_dto(return_dto)
        job: JobDataclass = job_db_service.get_job_by_id(return_dto.id)
        test_utils.check_if_job_finished(job)
        test_utils.check_if_job_runner_result_correct_multiple_gates(job)
