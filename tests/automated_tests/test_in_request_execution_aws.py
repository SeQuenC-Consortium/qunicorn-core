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
from qunicorn_core.core.jobmanager import jobmanager_service
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.result import ResultDataclass
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
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, ProviderName.AWS, True)
        return_dto: SimpleJobDto = jobmanager_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)
        # THEN: Check if the correct job with its result is saved in the db
        assert return_dto.job_state == JobState.RUNNING


def test_get_results_from_aws_local_simulator_job():
    """creates a new job again and tests the result of the aws local simulator in the db"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()
    # WHEN: create_and_run executed
    with app.app_context():
        job_request_dto: JobRequestDto = test_utils.get_test_job(ProviderName.AWS)
        test_utils.save_deployment_and_add_id_to_job(job_request_dto, ProviderName.AWS, True)
        return_dto: SimpleJobDto = jobmanager_service.create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)
        results: list[ResultDataclass] = job_db_service.get_job(return_dto.id).results
        print(results)
    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        assert check_aws_local_simulator_results(results[0].result_dict, job_request_dto.shots)


def check_aws_local_simulator_results(results_dict: dict, shots: int):
    is_check_successful = True
    counts: Counter = results_dict.get("counts")
    probabilities: dict = results_dict.get("probabilities")
    tolerance: int = 100
    condition1 = shots / 2 - tolerance < counts.get("000") < shots / 2 + tolerance
    condition2 = shots / 2 - tolerance < counts.get("111") < shots / 2 + tolerance
    if not (condition1 and condition2):
        is_check_successful = False
    elif not (0.48 < probabilities.get("000") < 0.52 and 0.48 < probabilities.get("111") < 0.52):
        is_check_successful = False
    return is_check_successful
