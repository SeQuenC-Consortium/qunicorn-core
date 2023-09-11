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
from collections import Counter

from qunicorn_core.api.api_models.job_dtos import SimpleJobDto, JobRequestDto
from qunicorn_core.core import job_service
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils
from tests.conftest import set_up_env

IS_ASYNCHRONOUS: bool = False
RESULT_TOLERANCE: int = 100


def test_create_and_run_aws_local_simulator():
    """Tests the create and run job method for synchronous execution of the aws local simulator"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()

    # WHEN: create_and_run executed
    with app.app_context():
        job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.AWS)
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QASM3)
        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

        # THEN: Check if the correct job with its result is saved in the db
        assert return_dto.state == JobState.RUNNING


def test_aws_local_simulator_braket_job_results():
    """creates a new job and a braket deployment from json input (from test resources) and runs it on the aws
    local_simulator.
    Then the results in the db are checked."""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()
    with app.app_context():
        # WHEN: create_and_run executed in generic_test
        results, shots = test_utils.generic_test(app, ProviderName.AWS, AssemblerLanguage.BRAKET, IS_ASYNCHRONOUS)
        # THEN: Check if the correct job with its result is saved in the db with results with a RESULT_TOLERANCE
        assert check_aws_local_simulator_results(results, shots)


def test_aws_local_simulator_qiskit_job_results():
    """creates a new job and a qiskit deployment from json input (from test resources) and runs it on the aws
    local_simulator.
    Then the results in the db are checked."""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()
    with app.app_context():
        # WHEN: create_and_run executed in generic_test
        results, shots = test_utils.generic_test(app, ProviderName.AWS, AssemblerLanguage.QISKIT, IS_ASYNCHRONOUS)
        # THEN: Check if the correct job with its result is saved in the db with results with a RESULT_TOLERANCE
        assert check_aws_local_simulator_results(results, shots)


def test_aws_local_simulator_qasm3_job_results():
    """creates a new job and a qasm3 deployment from json input (from test resources) and runs it on the aws
    local_simulator.
    Then the results in the db are checked."""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()
    with app.app_context():
        # WHEN: create_and_run executed in generic_test
        results, shots = test_utils.generic_test(app, ProviderName.AWS, AssemblerLanguage.QASM3, IS_ASYNCHRONOUS)
        # THEN: Check if the correct job with its result is saved in the db with results with a RESULT_TOLERANCE
        assert check_aws_local_simulator_results(results, shots)


def test_aws_local_simulator_qasm2_job_results():
    """creates a new job and a qasm2 deployment from json input (from test resources) and runs it on the aws
    local_simulator.
    Then the results in the db are checked."""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()
    with app.app_context():
        # WHEN: create_and_run executed in generic_test
        results, shots = test_utils.generic_test(app, ProviderName.AWS, AssemblerLanguage.QASM2, IS_ASYNCHRONOUS)
        # THEN: Check if the correct job with its result is saved in the db with results with a RESULT_TOLERANCE
        assert check_aws_local_simulator_results(results, shots)


def check_aws_local_simulator_results(results, shots: int):
    is_check_successful = True
    for i in range(len(results)):
        results_dict = results[i].result_dict
        counts: Counter = results_dict.get("counts")
        probabilities: dict = results_dict.get("probabilities")
        if i == 0:
            if counts.get("00") is not None and counts.get("11") is not None:
                counts0 = counts.get("00")
                probabilities0 = probabilities.get("00")
                counts1 = counts.get("11")
                probabilities1 = probabilities.get("11")
            else:
                raise AssertionError
            condition1 = shots / 2 - RESULT_TOLERANCE < counts0 < shots / 2 + RESULT_TOLERANCE
            condition2 = shots / 2 - RESULT_TOLERANCE < counts1 < shots / 2 + RESULT_TOLERANCE
            if not (condition1 and condition2):
                is_check_successful = False
            elif not (0.48 < probabilities0 < 0.52 and 0.48 < probabilities1 < 0.52):
                is_check_successful = False
        else:
            if counts.get("00") != shots:
                is_check_successful = False
    return is_check_successful
