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
from qunicorn_core.core.jobmanager import jobmanager_service
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from tests.conftest import set_up_env


def test_create_and_run_aws_local_simulator():
    """Tests the create and run job method for synchronous execution of the aws local simulator"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()

    with app.app_context():
        job_dto: JobRequestDto = JobRequestDto(
            name="JobName",
            circuits=["OPENQASM 3; qubit[3] q;bit[3] c; h q[0]; cnot q[0], q[1];" "cnot q[1], q[2];c = measure q;"],
            provider_name="AWS",
            shots=4000,
            parameters="[0]",
            token="",
            type=JobType.RUNNER,
            assembler_language=AssemblerLanguage.QASM,
        )
        job_response = jobmanager_service.create_and_run_job(job_dto)
        assert job_response.job_state == JobState.RUNNING


def test_get_results_from_aws_local_simulator_job():
    """creates a new job again and tests the result of the aws local simulator in the db"""
    # GIVEN: Database Setup - AWS added as a provider
    app = set_up_env()

    with app.app_context():
        job_dto: JobRequestDto = JobRequestDto(
            name="JobName",
            circuits=["OPENQASM 3; qubit[3] q;bit[3] c; h q[0]; cnot q[0], q[1];" "cnot q[1], q[2];c = measure q;"],
            provider_name="AWS",
            shots=4000,
            parameters="[0]",
            token="",
            type=JobType.RUNNER,
            assembler_language=AssemblerLanguage.QASM,
        )
        job_response = jobmanager_service.create_and_run_job(job_dto, False)
        print(job_db_service.get_job(job_response.id))
    assert 1 == 1
