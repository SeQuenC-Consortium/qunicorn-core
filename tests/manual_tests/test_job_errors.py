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
from qiskit.qasm import QasmError
from qiskit_ibm_provider.accounts import InvalidAccountError
from qiskit_ibm_provider.api.exceptions import RequestsApiError

from qunicorn_core.api.api_models import JobRequestDto
from qunicorn_core.core.jobmanager import jobmanager_service
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.result_type import ResultType
from tests.conftest import set_up_env
from tests.manual_tests.test_jobmanager_with_ibm import EXPECTED_ID, JOB_FINISHED_PROGRESS, IS_ASYNCHRONOUS
from tests.test_utils import get_object_from_json


def test_invalid_token():
    """Testing the synchronous call of the create_and_run_job with an invalid token"""
    # GIVEN: Create JobRequestDto with an invalid token
    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_test_data.json"))
    job_request_dto.device_name = "ibmq_qasm_simulator"
    job_request_dto.token = "Invalid Token"

    # WHEN: Executing create and run
    with app.app_context():
        with pytest.raises(Exception) as exception:
            jobmanager_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Test if correct Error was thrown and job is saved in db with error
    with app.app_context():
        assert RequestsApiError.__name__ in str(exception) or InvalidAccountError.__name__ in str(exception)
        assert job_finished_with_error()


def test_invalid_circuit():
    """Testing the synchronous call of the create_and_run_job with an invalid circuit (a correct token is needed)"""
    # GIVEN: Create JobRequestDto with an invalid circuit
    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_test_data.json"))
    job_request_dto.device_name = "ibmq_qasm_simulator"
    job_request_dto.circuits[0] = "Invalid Circuit"

    # WHEN: Executing create and run
    with app.app_context():
        with pytest.raises(Exception) as exception:
            jobmanager_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Test if QasmError was thrown and job is saved in db with error
    with app.app_context():
        assert QasmError.__name__ in str(exception)
        assert job_finished_with_error()


def test_invalid_token_for_sampler():
    """Testing the synchronous call of the create_and_run_job with an invalid token and the job type sampler"""
    # GIVEN: Create JobRequestDto with an invalid token and job type sampler
    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_test_data.json"))
    job_request_dto.device_name = "ibmq_qasm_simulator"
    job_request_dto.token = "Invalid Token"
    job_request_dto.type = JobType.SAMPLER

    # WHEN: Executing create and run
    with app.app_context():
        with pytest.raises(Exception) as exception:
            jobmanager_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Test if correct Error was thrown and job is saved in db with error
    with app.app_context():
        assert RequestsApiError.__name__ in str(exception) or InvalidAccountError.__name__ in str(exception)
        assert job_finished_with_error()


def job_finished_with_error() -> bool:
    job: JobDataclass = job_db_service.get_job(EXPECTED_ID)
    is_job_state_error: bool = job.state == JobState.ERROR
    is_result_type_error: bool = job.results[0].result_type == ResultType.ERROR
    is_progress_hundred: bool = job.progress == JOB_FINISHED_PROGRESS
    return is_job_state_error and is_result_type_error and is_progress_hundred
