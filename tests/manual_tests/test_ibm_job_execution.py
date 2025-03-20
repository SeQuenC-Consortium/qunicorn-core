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

""" "Test class to test the functionality of the job_api"""

from qunicorn_core.api.api_models import JobRequestDto, SimpleJobDto
from qunicorn_core.core import job_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils
from tests.automated_tests import test_ibm_sampler
from tests.conftest import set_up_env
from tests.test_utils import IS_ASYNCHRONOUS, PROBABILITY_1, PROBABILITY_TOLERANCE


def test_create_and_run_runner_with_qiskit():
    test_utils.execute_job_test(ProviderName.IBM, "ibmq_qasm_simulator", [AssemblerLanguage.QISKIT])


def test_create_and_run_runner_with_qasm2():
    test_utils.execute_job_test(ProviderName.IBM, "ibmq_qasm_simulator", [AssemblerLanguage.QASM2])


def test_create_and_run_runner_with_qasm3():
    test_utils.execute_job_test(ProviderName.IBM, "ibmq_qasm_simulator", [AssemblerLanguage.QASM3])


def test_create_and_run_runner_with_braket():
    test_utils.execute_job_test(ProviderName.IBM, "ibmq_qasm_simulator", [AssemblerLanguage.BRAKET])


def test_create_and_run_runner_with_qrisp():
    test_utils.execute_job_test(ProviderName.IBM, "ibmq_qasm_simulator", [AssemblerLanguage.QRISP])


def test_create_and_run_sampler():
    test_ibm_sampler.create_and_run_sampler_with_device("ibmq_qasm_simulator")


def test_create_and_run_estimator():
    """Tests the create and run job method for synchronous execution of an estimator"""
    # GIVEN: Database Setup & job_request_dto created
    app = set_up_env()
    job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.IBM)
    job_request_dto.type = JobType.ESTIMATOR
    job_request_dto.device_name = "ibmq_qasm_simulator"

    # WHEN: create_and_run executed synchronous
    with app.app_context():
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, [AssemblerLanguage.QASM2])
        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        test_utils.check_simple_job_dto(return_dto)
        job: JobDataclass = JobDataclass.get_by_id_or_404(return_dto.id)
        test_utils.check_if_job_finished(job)
        check_if_job_estimator_result_correct(job)


def check_if_job_estimator_result_correct(job: JobDataclass):
    job.type = JobType.ESTIMATOR
    for i in range(len(job.results)):
        result: ResultDataclass = job.results[i]
        test_utils.check_standard_result_data(i, job, result)
        assert result.meta_data is not None
        assert -PROBABILITY_TOLERANCE < float(result.result_dict["value"]) < PROBABILITY_TOLERANCE
        assert PROBABILITY_1 - PROBABILITY_TOLERANCE < float(result.result_dict["variance"]) <= PROBABILITY_1
