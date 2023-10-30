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

import pytest
from qiskit_ibm_provider.accounts import InvalidAccountError
from qiskit_ibm_provider.api.exceptions import RequestsApiError

from qunicorn_core.api.api_models import JobRequestDto, DeploymentRequestDto
from qunicorn_core.core import job_service
from qunicorn_core.core.mapper import deployment_mapper
from qunicorn_core.db.database_services import job_db_service, db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.result_type import ResultType
from tests import test_utils
from tests.conftest import set_up_env
from tests.test_utils import EXPECTED_ID, JOB_FINISHED_PROGRESS, IS_ASYNCHRONOUS, get_object_from_json


def test_invalid_token():
    """Testing the synchronous call of the create_and_run_job with an invalid token"""
    # GIVEN: Create JobRequestDto with an invalid token
    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_ibm_test_data.json"))
    job_request_dto.device_name = "ibmq_qasm_simulator"
    job_request_dto.token = "Invalid Token"

    # WHEN: Executing create and run
    exception = create_deployment_run_job_return_exception(app, job_request_dto)

    # THEN: Test if correct Error was thrown and job is saved in db with error
    with app.app_context():
        assert RequestsApiError.__name__ in str(exception) or InvalidAccountError.__name__ in str(exception)
        assert job_finished_with_error()


def test_invalid_circuit():
    """Testing the synchronous call of the create_and_run_job with an invalid circuit (a correct token is needed)"""
    # GIVEN: Create JobRequestDto with an invalid circuit
    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_ibm_test_data.json"))
    job_request_dto.device_name = "ibmq_qasm_simulator"
    deployment_dto: DeploymentRequestDto = test_utils.get_test_deployment_request([AssemblerLanguage.QISKIT])
    deployment_dto.programs[0].quantum_circuit = "invalid circuit"

    # WHEN: Executing create and run
    with app.app_context():
        deployment: DeploymentDataclass = deployment_mapper.request_to_dataclass(deployment_dto)
        deployment.deployed_by = None
        deployment_id: int = db_service.save_database_object(deployment).id
        job_request_dto.deployment_id = deployment_id
        with pytest.raises(Exception) as exception:
            job_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Test if QasmError was thrown and job is saved in db with error
    with app.app_context():
        assert "TranspileError" in str(exception)
        assert job_finished_with_error()


def create_deployment_run_job_return_exception(app, job_request_dto):
    """Creating an exception for the job errors"""
    with app.app_context():
        with pytest.raises(Exception) as exception:
            test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QASM2)
            job_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)
    return exception


def job_finished_with_error() -> bool:
    job: JobDataclass = job_db_service.get_job_by_id(EXPECTED_ID)
    is_job_state_error: bool = job.state == JobState.ERROR
    is_result_type_error: bool = job.results[0].result_type == ResultType.ERROR
    is_progress_hundred: bool = job.progress == JOB_FINISHED_PROGRESS
    return is_job_state_error and is_result_type_error and is_progress_hundred
