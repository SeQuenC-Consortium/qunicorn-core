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
from unittest.mock import Mock, MagicMock, patch

import yaml
from qiskit_ibm_runtime import QiskitRuntimeService

from qunicorn_core.api.api_models import JobRequestDto, JobCoreDto, QuantumProgramDto
from qunicorn_core.core.jobmanager.jobmanager_service import run_job
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.core.programmanager import programmanager_service
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from tests.conftest import set_up_env
from tests.test_utils import get_object_from_json


def test_celery_run_job(mocker):
    """Testing the synchronous call of the run_job celery task"""
    # GIVEN: Setting up Mocks and Environment
    backend_mock = Mock()
    run_result_mock = Mock()

    run_result_mock.result.return_value = Mock()  # mocks the job_from_ibm.result() call
    backend_mock.run.return_value = run_result_mock  # mocks the backend.run(transpiled, shots=job_dto.shots) call

    path_to_pilot: str = "qunicorn_core.core.pilotmanager.qiskit_pilot.QiskitPilot"
    mocker.patch(f"{path_to_pilot}._QiskitPilot__get_ibm_provider_and_login", return_value=backend_mock)
    mocker.patch(f"{path_to_pilot}.transpile", return_value=(backend_mock, None))

    results: list[ResultDataclass] = [ResultDataclass(result_dict={"00": 4000})]
    mocker.patch("qunicorn_core.core.mapper.result_mapper.runner_result_to_db_results", return_value=results)

    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_test_data.json"))

    # WHEN: Executing method to be tested
    with app.app_context():
        job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
        job: JobDataclass = job_db_service.create_database_job(job_core_dto)
        job_core_dto.id = job.id
        serialized_job_core_dto = yaml.dump(job_core_dto)
        # Calling the Method to be tested synchronously
        run_job({"data": serialized_job_core_dto})

    # THEN: Test Assertion
    with app.app_context():
        new_job = job_db_service.get_job(job_core_dto.id)
        assert new_job.state == JobState.FINISHED


def test_celery_run_job_for_ibm_upload(mocker):
    """Testing the synchronous call of the run_job celery task for ibm file upload"""
    # GIVEN: Setting up Mocks and Environment
    path_to_service: str = "qiskit_ibm_runtime.qiskit_runtime_service.QiskitRuntimeService"
    mocker.patch(f"{path_to_service}.save_account", return_value=None)
    mocker.patch(f"{path_to_service}.upload_program", return_value="test-id")
    mocker.patch(f"{path_to_service}.run", return_value=None)

    app = set_up_env()

    quantum_program_dto: QuantumProgramDto = QuantumProgramDto(**get_object_from_json("program_request_dto_test_data.json"))
    with app.app_context():
        result_program: QuantumProgramDataclass = programmanager_service.create_database_program(quantum_program_dto)
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_test_data.json"))
    job_request_dto.type = JobType.FILE
    job_request_dto.programs = [result_program.id]

    # WHEN: Executing method to be tested
    with app.app_context():
        job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
        job: JobDataclass = job_db_service.create_database_job(job_core_dto)
        job_core_dto.id = job.id
        serialized_job_core_dto = yaml.dump(job_core_dto)
        # Calling the Method to be tested synchronously
        run_job({"data": serialized_job_core_dto})

    # THEN: Test Assertion
    with app.app_context():
        new_job = job_db_service.get_job(job_core_dto.id)
        assert new_job.state == JobState.FINISHED
