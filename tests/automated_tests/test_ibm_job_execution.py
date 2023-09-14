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
from unittest.mock import Mock

import pytest
import yaml
from qiskit_ibm_runtime import IBMRuntimeError

from qunicorn_core.api.api_models import JobRequestDto, JobCoreDto
from qunicorn_core.core.job_manager_service import run_job
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils
from tests.conftest import set_up_env

IS_ASYNCHRONOUS: bool = False


def __test_celery_run_job(mocker):
    """Testing the synchronous call of the run_job celery task"""
    # GIVEN: Setting up Mocks and Environment
    backend_mock = Mock()
    run_result_mock = Mock()

    run_result_mock.result.return_value = Mock()  # mocks the job_from_ibm.result() call
    backend_mock.run.return_value = run_result_mock  # mocks the backend.run(transpiled, shots=job_dto.shots) call

    path_to_pilot: str = "qunicorn_core.core.pilotmanager.ibm_pilot.IBMPilot"
    mocker.patch(f"{path_to_pilot}._IBMPilot__get_ibm_provider_login_and_update_job", return_value=backend_mock)
    mocker.patch(f"{path_to_pilot}.transpile", return_value=(backend_mock, None))

    results: list[ResultDataclass] = [ResultDataclass(result_dict={"00": 4000})]
    mocker.patch("qunicorn_core.core.mapper.result_mapper.ibm_runner_to_dataclass", return_value=results)

    app = set_up_env()
    job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.IBM)
    job_request_dto.device_name = "ibmq_qasm_simulator"

    # WHEN: Executing method to be tested
    with app.app_context():
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QASM2)
        job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
        job: JobDataclass = job_db_service.create_database_job(job_core_dto)
        job_core_dto.id = job.id
        serialized_job_core_dto = yaml.dump(job_core_dto)
        # Calling the Method to be tested synchronously
        run_job({"data": serialized_job_core_dto})

    # THEN: Test Assertion
    with app.app_context():
        new_job = job_db_service.get_job_by_id(job_core_dto.id)
        assert new_job.state == JobState.FINISHED


def __test_job_ibm_upload(mocker):
    """Testing the synchronous call of the upload of a file to IBM"""
    # GIVEN: Setting up Mocks and Environment
    mock = Mock()
    mock.upload_program.return_value = "test-id"
    mock.run.return_value = None
    path_to_pilot: str = "qunicorn_core.core.pilotmanager.ibm_pilot.IBMPilot"
    mocker.patch(f"{path_to_pilot}._IBMPilot__get_runtime_service", return_value=mock)

    app = set_up_env()
    job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.IBM)
    job_request_dto.type = JobType.IBM_UPLOAD
    job_request_dto.device_name = "ibmq_qasm_simulator"

    # WHEN: Executing method to be tested
    with app.app_context():
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QISKIT)
        job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
        job: JobDataclass = job_db_service.create_database_job(job_core_dto)
        job_core_dto.id = job.id
        serialized_job_core_dto = yaml.dump(job_core_dto)
        # Calling the Method to be tested synchronously
        run_job({"data": serialized_job_core_dto})

    # THEN: Test Assertion
    with app.app_context():
        new_job = job_db_service.get_job_by_id(job_core_dto.id)
        assert new_job.state == JobState.READY


def __test_job_ibm_runner(mocker):
    """Testing the synchronous call of the execution of an upload file to IBM"""
    # GIVEN: Setting up Mocks and Environment
    mock = Mock()
    mock.upload_program.return_value = "test-id"  # Returning an id value after uploading a file to IBM
    mock.run.side_effect = IBMRuntimeError
    path_to_pilot: str = "qunicorn_core.core.pilotmanager.ibm_pilot.IBMPilot"
    mocker.patch(f"{path_to_pilot}._IBMPilot__get_runtime_service", return_value=mock)

    app = set_up_env()
    job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.IBM)
    job_request_dto.type = JobType.IBM_UPLOAD
    job_request_dto.device_name = "ibmq_qasm_simulator"

    with app.app_context():
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QISKIT)
        job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
        job: JobDataclass = job_db_service.create_database_job(job_core_dto)
        job_core_dto.id = job.id
        serialized_job_core_dto = yaml.dump(job_core_dto)
        # Calling the Method to be tested synchronously
        run_job({"data": serialized_job_core_dto})

    # WHEN: Executing method to be tested
    with app.app_context():
        job: JobDataclass = job_db_service.get_job_by_id(job_core_dto.id)
        job_core: JobCoreDto = job_mapper.dataclass_to_core(job)
        job_core.ibm_file_options = {"backend": "ibmq_qasm_simulator"}
        job_core.ibm_file_inputs = {"my_obj": "MyCustomClass(my foo, my bar)"}
        serialized_job_core_dto = yaml.dump(job_core)
        with pytest.raises(IBMRuntimeError):
            run_job({"data": serialized_job_core_dto})

    # THEN: Test Assertion
    with app.app_context():
        new_job = job_db_service.get_job_by_id(job_core_dto.id)
        assert new_job.state == JobState.ERROR


def test_create_and_run_job_on_aer_simulator_with_qiskit():
    """Tests the create and run job method for synchronous execution of a runner on aer simulator"""
    app = set_up_env()

    test_utils.generic_test(app, ProviderName.IBM, "aer_simulator", AssemblerLanguage.QISKIT, IS_ASYNCHRONOUS)


def test_create_and_run_job_on_aer_simulator_with_qasm2():
    """Tests the create and run job method for synchronous execution of a runner on aer simulator"""
    app = set_up_env()

    test_utils.generic_test(app, ProviderName.IBM, "aer_simulator", AssemblerLanguage.QASM2, IS_ASYNCHRONOUS)


def test_create_and_run_job_on_aer_simulator_with_qasm3():
    """Tests the create and run job method for synchronous execution of a runner on aer simulator"""
    app = set_up_env()

    test_utils.generic_test(app, ProviderName.IBM, "aer_simulator", AssemblerLanguage.QASM3, IS_ASYNCHRONOUS)


def test_create_and_run_job_on_aer_simulator_with_braket():
    """Tests the create and run job method for synchronous execution of a runner on aer simulator"""
    app = set_up_env()

    test_utils.generic_test(app, ProviderName.IBM, "aer_simulator", AssemblerLanguage.BRAKET, IS_ASYNCHRONOUS)
