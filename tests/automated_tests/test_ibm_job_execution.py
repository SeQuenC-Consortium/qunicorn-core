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

"""Test class to test the functionality of the job_api"""

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils
from tests.test_utils import IBM_LOCAL_SIMULATOR


def test_create_and_run_job_on_aer_simulator_with_qiskit():
    test_utils.execute_job_test(ProviderName.IBM, IBM_LOCAL_SIMULATOR, [AssemblerLanguage.QISKIT])


def test_create_and_run_job_on_aer_simulator_with_qasm2():
    test_utils.execute_job_test(ProviderName.IBM, IBM_LOCAL_SIMULATOR, [AssemblerLanguage.QASM2])


def test_create_and_run_job_on_aer_simulator_with_qasm3():
    test_utils.execute_job_test(ProviderName.IBM, IBM_LOCAL_SIMULATOR, [AssemblerLanguage.QASM3])


def test_create_and_run_job_on_aer_simulator_with_braket():
    test_utils.execute_job_test(ProviderName.IBM, IBM_LOCAL_SIMULATOR, [AssemblerLanguage.BRAKET])


def test_create_and_run_job_on_aer_simulator_with_qrisp():
    test_utils.execute_job_test(ProviderName.IBM, IBM_LOCAL_SIMULATOR, [AssemblerLanguage.QRISP])


"""Test for experimental ibm_upload"""
# def __test_job_ibm_upload(mocker):
#    """Testing the synchronous call of the upload of a file to IBM"""
#    # GIVEN: Setting up Mocks and Environment
#    mock = Mock()
#    mock.upload_program.return_value = "test-id"
#    mock.run.return_value = None
#    path_to_pilot: str = "qunicorn_core.core.pilotmanager.ibm_pilot.IBMPilot"
#    mocker.patch(f"{path_to_pilot}._IBMPilot__get_runtime_service", return_value=mock)
#
#    app = set_up_env()
#    job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.IBM)
#    job_request_dto.type = JobType.IBM_UPLOAD
#    job_request_dto.device_name = "ibmq_qasm_simulator"
#
#    # WHEN: Executing method to be tested
#    with app.app_context():
#        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QISKIT)
#        job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
#        job: JobDataclass = job_db_service.create_database_job(job_core_dto)
#        job_core_dto.id = job.id
#        serialized_job_core_dto = yaml.dump(job_core_dto)
#        # Calling the Method to be tested synchronously
#        run_job({"data": serialized_job_core_dto})
#
#    # THEN: Test Assertion
#    with app.app_context():
#        new_job = job_db_service.get_job_by_id(job_core_dto.id)
#        assert new_job.state == JobState.READY

"""Test for experimental ibm_runner"""
# def __test_job_ibm_runner(mocker):
#    """Testing the synchronous call of the execution of an upload file to IBM"""
#    # GIVEN: Setting up Mocks and Environment
#    mock = Mock()
#    mock.upload_program.return_value = "test-id"  # Returning an id value after uploading a file to IBM
#    mock.run.side_effect = IBMRuntimeError
#    path_to_pilot: str = "qunicorn_core.core.pilotmanager.ibm_pilot.IBMPilot"
#    mocker.patch(f"{path_to_pilot}._IBMPilot__get_runtime_service", return_value=mock)

#    app = set_up_env()
#    job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.IBM)
#    job_request_dto.type = JobType.IBM_UPLOAD
#    job_request_dto.device_name = "ibmq_qasm_simulator"

#    with app.app_context():
#        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QISKIT)
#        job_core_dto: JobCoreDto = job_mapper.request_to_core(job_request_dto)
#        job: JobDataclass = job_db_service.create_database_job(job_core_dto)
#        job_core_dto.id = job.id
#        serialized_job_core_dto = yaml.dump(job_core_dto)
#        # Calling the Method to be tested synchronously
#        run_job({"data": serialized_job_core_dto})
#
#    # WHEN: Executing method to be tested
#    with app.app_context():
#        job: JobDataclass = job_db_service.get_job_by_id(job_core_dto.id)
#        job_core: JobCoreDto = job_mapper.dataclass_to_core(job)
#        job_core.ibm_file_options = {"backend": "ibmq_qasm_simulator"}
#        job_core.ibm_file_inputs = {"my_obj": "MyCustomClass(my foo, my bar)"}
#        serialized_job_core_dto = yaml.dump(job_core)
#        with pytest.raises(IBMRuntimeError):
#            run_job({"data": serialized_job_core_dto})
#
#    # THEN: Test Assertion
#    with app.app_context():
#        new_job = job_db_service.get_job_by_id(job_core_dto.id)
#        assert new_job.state == JobState.ERROR
