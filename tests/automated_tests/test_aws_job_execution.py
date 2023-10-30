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

"""test in-request execution for aws"""

from qunicorn_core.api.api_models.job_dtos import SimpleJobDto, JobRequestDto
from qunicorn_core.core import job_service
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils
from tests.conftest import set_up_env

IS_ASYNCHRONOUS: bool = False
RESULT_TOLERANCE: int = 100


def test_aws_local_simulator_braket_job_results():
    test_utils.execute_job_test(ProviderName.AWS, "local_simulator", [AssemblerLanguage.BRAKET])


def test_aws_local_simulator_qiskit_job_results():
    test_utils.execute_job_test(ProviderName.AWS, "local_simulator", [AssemblerLanguage.QISKIT])


def test_aws_local_simulator_qasm3_job_results():
    test_utils.execute_job_test(ProviderName.AWS, "local_simulator", [AssemblerLanguage.QASM3])


def test_aws_local_simulator_qasm2_job_results():
    test_utils.execute_job_test(ProviderName.AWS, "local_simulator", [AssemblerLanguage.QASM2])


def test_create_and_run_aws_local_simulator():
    """Tests the create and run job method for synchronous execution of the aws local simulator"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()

    # WHEN: create_and_run executed
    with app.app_context():
        job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.AWS)
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, [AssemblerLanguage.QASM3])

        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto)

        # THEN: Check if the correct job with its result is saved in the db
        assert return_dto.state == JobState.READY
