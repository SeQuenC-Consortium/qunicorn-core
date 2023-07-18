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

import yaml

from qunicorn_core.api.api_models import JobRequestDto, JobCoreDto
from qunicorn_core.core.jobmanager.jobmanager_service import run_job
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.job_state import JobState
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
