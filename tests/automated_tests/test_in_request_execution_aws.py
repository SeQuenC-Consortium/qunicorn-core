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


def test_aws_local_simulator_qasm3_job_results():
    """creates a new job and tests the result of the aws local simulator in the db with a qasm3 circuit"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()

    # WHEN: create_and_run executed
    with app.app_context():
        job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.AWS)
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QASM3)
        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)
        results: list[ResultDataclass] = job_db_service.get_job_by_id(return_dto.id).results

    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        assert check_aws_local_simulator_results(results, job_request_dto.shots)


def test_aws_local_simulator_braket_job_results():
    """creates a new job and tests the result of the aws local simulator in the db with a braket circuit"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()

    # WHEN: create_and_run executed
    with app.app_context():
        job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.AWS)
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.BRAKET)
        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)
        results: list[ResultDataclass] = job_db_service.get_job_by_id(return_dto.id).results

    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        print(results)
        assert check_aws_local_simulator_results(results, job_request_dto.shots)


def test_aws_local_simulator_qiskit_job_results():
    """creates a new job and tests the result of the aws local simulator in the db with a qiskit circuit"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()

    # WHEN: create_and_run executed
    with app.app_context():
        job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.AWS)
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, AssemblerLanguage.QISKIT)
        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)
        results: list[ResultDataclass] = job_db_service.get_job_by_id(return_dto.id).results

    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        assert check_aws_local_simulator_results(results, job_request_dto.shots)


def check_aws_local_simulator_results(results, shots: int):
    is_check_successful = True
    for i in range(len(results)):
        results_dict = results[i].result_dict
        counts: Counter = results_dict.get("counts")
        probabilities: dict = results_dict.get("probabilities")
        tolerance: int = 100
        if i == 0:
            if counts.get("00") is not None and counts.get("11") is not None:
                counts0 = counts.get("00")
                probabilities0 = probabilities.get("00")
                counts1 = counts.get("11")
                probabilities1 = probabilities.get("11")
            else:
                raise AssertionError
            condition1 = shots / 2 - tolerance < counts0 < shots / 2 + tolerance
            condition2 = shots / 2 - tolerance < counts1 < shots / 2 + tolerance
            if not (condition1 and condition2):
                is_check_successful = False
            elif not (0.48 < probabilities0 < 0.52 and 0.48 < probabilities1 < 0.52):
                is_check_successful = False
        else:
            if counts.get("00") != shots:
                is_check_successful = False
    return is_check_successful
