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
import json
import os
from unittest.mock import Mock

import yaml

from qunicorn_core import create_app
from qunicorn_core.api.api_models import JobRequestDto, JobCoreDto
from qunicorn_core.core.jobmanager.jobmanager_service import run_job
from qunicorn_core.core.mapper import job_mapper
from qunicorn_core.db.cli import create_db_function
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState

DEFAULT_TEST_CONFIG = {
    "SECRET_KEY": "test",
    "DEBUG": False,
    "TESTING": True,
    "JSON_SORT_KEYS": True,
    "JSONIFY_PRETTYPRINT_REGULAR": False,
    "DEFAULT_LOG_FORMAT_STYLE": "{",
    "DEFAULT_LOG_FORMAT": "{asctime} [{levelname:^7}] [{module:<30}] {message}    <{funcName}, {lineno}; {pathname}>",
    "DEFAULT_FILE_STORE": "local_filesystem",
    "FILE_STORE_ROOT_PATH": "files",
    "OPENAPI_VERSION": "3.0.2",
    "OPENAPI_JSON_PATH": "api-spec.json",
    "OPENAPI_URL_PREFIX": "",
}


def set_up_env():
    """Set up Flask app and environment and return app"""
    test_config = {}
    test_config.update(DEFAULT_TEST_CONFIG)
    test_config.update({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    app = create_app(test_config)
    with app.app_context():
        create_db_function(app)

    return app


def test_celery_run_job(mocker):
    """Testing the synchronous call of the run_job celery task"""
    # GIVEN: Setting up Mocks and Environment
    backend_mock = Mock()
    run_result_mock = Mock()
    get_result_mock = Mock()
    get_result_mock.get_counts.return_value = 1000
    run_result_mock.result.return_value = get_result_mock
    backend_mock.run.return_value = run_result_mock

    mocker.patch("qunicorn_core.core.pilotmanager.qiskit_pilot.QiskitPilot._QiskitPilot__get_ibm_provider", return_value=backend_mock)
    mocker.patch("qunicorn_core.core.pilotmanager.qiskit_pilot.QiskitPilot.transpile", return_value=(backend_mock, None))

    app = set_up_env()

    # WHEN: Executing method to be tested
    root_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = "../job_test_data.json"
    path_dir = "{}{}{}".format(root_dir, os.sep, file_name)

    with open(path_dir) as f:
        data = json.load(f)
    with app.app_context():
        job_dto: JobRequestDto = JobRequestDto(**data)
        job_core_dto: JobCoreDto = job_mapper.request_to_core(job_dto)
        job: JobDataclass = job_db_service.create_database_job(job_core_dto)
        job_core_dto.id = job.id
        serialized_job_core_dto = yaml.dump(job_core_dto)
        # Calling the Method to be tested synchronously
        run_job({"data": serialized_job_core_dto})

    # THEN: Test Assertion
    with app.app_context():
        new_job = job_db_service.get_job(1)
        assert new_job.state == JobState.FINISHED
