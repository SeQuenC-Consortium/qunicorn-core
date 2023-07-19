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

from qunicorn_core.api.api_models import JobRequestDto, SimpleJobDto
from qunicorn_core.core.jobmanager.jobmanager_service import create_and_run_job
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.result_type import ResultType
from tests.conftest import set_up_env
from tests.test_utils import get_object_from_json

EXPECTED_ID: int = 2
JOB_FINISHED_PROGRESS: int = 100
STANDARD_JOB_NAME: str = "JobName"
IS_ASYNCHRONOUS: bool = False


def test_create_and_run_runner():
    """Tests the create and run job method for synchronous execution of a runner"""
    # GIVEN: Database Setup & job_request_dto created
    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_test_data.json"))
    job_request_dto.device_name = "ibmq_qasm_simulator"

    # WHEN: create_and_run executed synchronous
    with app.app_context():
        return_dto: SimpleJobDto = create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        check_simple_job_dto(return_dto)
        job: JobDataclass = job_db_service.get(return_dto.id)
        check_if_job_finished(job)
        check_if_job_runner_result_correct(job)


def test_create_and_run_sampler():
    """Tests the create and run job method for synchronous execution of a sampler"""
    # GIVEN: Database Setup & job_request_dto created
    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_test_data.json"))
    job_request_dto.type = JobType.SAMPLER
    job_request_dto.device_name = "ibmq_qasm_simulator"

    # WHEN: create_and_run executed synchronous
    with app.app_context():
        return_dto: SimpleJobDto = create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        check_simple_job_dto(return_dto)
        job: JobDataclass = job_db_service.get(return_dto.id)
        check_if_job_finished(job)
        check_if_job_sample_result_correct(job)


def test_create_and_run_estimator():
    """Tests the create and run job method for synchronous execution of an estimator"""
    # GIVEN: Database Setup & job_request_dto created
    app = set_up_env()
    job_request_dto: JobRequestDto = JobRequestDto(**get_object_from_json("job_request_dto_test_data.json"))
    job_request_dto.type = JobType.ESTIMATOR
    job_request_dto.device_name = "ibmq_qasm_simulator"

    # WHEN: create_and_run executed synchronous
    with app.app_context():
        return_dto: SimpleJobDto = create_and_run_job(job_request_dto, IS_ASYNCHRONOUS)

    # THEN: Check if the correct job with its result is saved in the db
    with app.app_context():
        check_simple_job_dto(return_dto)
        job: JobDataclass = job_db_service.get(return_dto.id)
        check_if_job_finished(job)
        check_if_job_estimator_result_correct(job)


def check_if_job_finished(job: JobDataclass):
    assert job.id == EXPECTED_ID
    assert job.progress == JOB_FINISHED_PROGRESS
    assert job.state == JobState.FINISHED


def check_simple_job_dto(return_dto: SimpleJobDto):
    assert return_dto.id == EXPECTED_ID
    assert return_dto.name == STANDARD_JOB_NAME
    assert return_dto.job_state == JobState.RUNNING


def check_if_job_sample_result_correct(job: JobDataclass):
    job.type = JobType.SAMPLER
    for i in range(len(job.results)):
        result: ResultDataclass = job.results[i]
        check_standard_result_data(i, job, result)
        assert result.meta_data is None
        default_dist: float = 1.0
        if i == 0:
            tolerance: float = 0.2
            assert (default_dist / 2 + tolerance) > result.result_dict["3"] > (default_dist / 2 - tolerance)
            assert (default_dist / 2 + tolerance) > result.result_dict["0"] > (default_dist / 2 - tolerance)
            assert round((result.result_dict["3"] + result.result_dict["0"])) == default_dist
        else:
            assert result.result_dict["0"] == default_dist


def check_if_job_runner_result_correct(job: JobDataclass):
    job.type = JobType.RUNNER
    for i in range(len(job.results)):
        result: ResultDataclass = job.results[i]
        check_standard_result_data(i, job, result)
        assert result.meta_data is not None
        shots: int = job.shots
        if i == 0:
            tolerance: int = 100
            assert (shots / 2 + tolerance) > result.result_dict["00"] > (shots / 2 - tolerance)
            assert (shots / 2 + tolerance) > result.result_dict["11"] > (shots / 2 - tolerance)
            assert (result.result_dict["00"] + result.result_dict["11"]) == shots
        else:
            assert result.result_dict["00"] == shots


def check_if_job_estimator_result_correct(job: JobDataclass):
    job.type = JobType.ESTIMATOR
    for i in range(len(job.results)):
        result: ResultDataclass = job.results[i]
        check_standard_result_data(i, job, result)
        assert result.meta_data is not None
        tolerance: float = 0.2
        default_variance: float = 1.0
        assert -tolerance < float(result.result_dict["value"]) < tolerance
        assert default_variance - tolerance < float(result.result_dict["variance"]) < default_variance


def check_standard_result_data(i, job, result):
    assert result.result_type == ResultType.get_result_type(job.type)
    assert result.job_id == job.id
    assert result.circuit == job.deployment.program_ids[i].quantum_circuit
