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

from qunicorn_core.api.api_models.job_dtos import SimpleJobDto
from qunicorn_core.api.job_api.job_view import JobIDView
from tests.conftest import set_up_env
from flask import jsonify


def test_create_and_run_aws_local_simulator():
    """Tests the create and run job method for synchronous execution of the aws local simulator"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()

    with app.app_context():
        result = JobIDView.post(
            '{"type": "AWS_SIMULATOR", "parameters": [0], "circuits": ["OPENQASM 3; \nqubit[3] q;\nbit[3] c;\
            \nh q[0]; \ncnot q[0], q[1];\ncnot q[1], q[2];\nc = measure q;"], "shots": 4000, "assemblerLanguage": "BRAKET", \
            "name": "JobName", "token": "", "providerName": "AWS"}'
        )

    with app.app_context():
        print(result)
        dto = SimpleJobDto(id=1, name="JobName", job_state="RUNNING")
        testresult = jsonify(dto, 200)
        assert result == testresult


test_create_and_run_aws_local_simulator()
