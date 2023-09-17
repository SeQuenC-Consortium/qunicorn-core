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

""""pytest utils file"""
import json
import os
from collections import Counter

from qunicorn_core.api.api_models import DeploymentRequestDto, JobRequestDto, DeploymentDto, SimpleJobDto
from qunicorn_core.core import deployment_service, job_service
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType

from tests.conftest import set_up_env

JOB_JSON_IBM = "job_request_dto_test_data_IBM.json"
JOB_JSON_AWS = "job_request_dto_test_data_AWS.json"
DEPLOYMENT_JSON = "deployment_request_dto_test_data.json"
DEPLOYMENT_QASM2_CIRCUITS_JSON = "deployment_request_dto_with_qasm2_circuit_test_data.json"
DEPLOYMENT_QASM3_CIRCUITS_JSON = "deployment_request_dto_with_qasm3_circuit_test_data.json"
DEPLOYMENT_BRAKET_CIRCUITS_JSON = "deployment_request_dto_with_braket_circuit_test_data.json"
DEPLOYMENT_QISKIT_CIRCUITS_JSON = "deployment_request_dto_with_qiskit_circuit_test_data.json"
PROGRAM_JSON = "program_request_dto_test_data.json"

EXPECTED_ID: int = 3  # hardcoded ID can be removed if tests for the correct ID are no longer needed
JOB_FINISHED_PROGRESS: int = 100
STANDARD_JOB_NAME: str = "JobName"
IS_ASYNCHRONOUS: bool = False
RESULT_TOLERANCE: int = 100



def execute_job_test(
    provider: ProviderName, device: str, input_assembler_language: AssemblerLanguage, is_asynchronous: bool = False
):
    """creates and runs a new job and checks the response"""

    # GIVEN: Database Setup
    app = set_up_env()

    with app.app_context():
        job_request_dto: JobRequestDto = get_test_job(provider)
        job_request_dto.device_name = device
        save_deployment_and_add_id_to_job(job_request_dto, input_assembler_language)

        # WHEN: create_and_run
        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto, is_asynchronous)

        # THEN: Check if the correct job with its result is saved in the db with results with a RESULT_TOLERANCE
        check_simple_job_dto(return_dto)
        job: JobDataclass = job_db_service.get_job_by_id(return_dto.id)
        check_if_job_finished(job)
        if provider is ProviderName.IBM:
            ibm_check_if_job_runner_result_correct(job)
        elif provider is ProviderName.AWS:
            check_aws_local_simulator_results(job.results, job.shots)


def get_object_from_json(json_file_name: str):
    """Returns the json object out of the json file with the name json_file_name"""
    resource_folder: str = "test_resources"

    root_dir = os.path.dirname(os.path.abspath(__file__))
    path_dir = "{}{}{}{}{}".format(root_dir, os.sep, resource_folder, os.sep, json_file_name)
    with open(path_dir) as f:
        data = json.load(f)
    return data


def save_deployment_and_add_id_to_job(job_request_dto: JobRequestDto, assembler_language):
    deployment_request: DeploymentRequestDto = get_test_deployment_request(assembler_language=assembler_language)
    deployment: DeploymentDto = deployment_service.create_deployment(deployment_request)
    job_request_dto.deployment_id = deployment.id


def get_test_deployment_request(assembler_language: AssemblerLanguage) -> DeploymentRequestDto:
    if assembler_language == AssemblerLanguage.QISKIT:
        deployment_dict: dict = get_object_from_json(DEPLOYMENT_QISKIT_CIRCUITS_JSON)
        return DeploymentRequestDto.from_dict(deployment_dict)
    elif assembler_language == AssemblerLanguage.QASM2:
        deployment_dict: dict = get_object_from_json(DEPLOYMENT_QASM2_CIRCUITS_JSON)
        return DeploymentRequestDto.from_dict(deployment_dict)
    if assembler_language == AssemblerLanguage.BRAKET:
        deployment_dict: dict = get_object_from_json(DEPLOYMENT_BRAKET_CIRCUITS_JSON)
        return DeploymentRequestDto.from_dict(deployment_dict)
    elif assembler_language == AssemblerLanguage.QASM3:
        deployment_dict: dict = get_object_from_json(DEPLOYMENT_QASM3_CIRCUITS_JSON)
        return DeploymentRequestDto.from_dict(deployment_dict)


def get_test_job(provider: ProviderName) -> JobRequestDto:
    if provider == ProviderName.IBM:
        job_dict: dict = get_object_from_json(JOB_JSON_IBM)
        return JobRequestDto(**job_dict)
    elif provider == ProviderName.AWS:
        job_dict: dict = get_object_from_json(JOB_JSON_AWS)
        return JobRequestDto(**job_dict)


def check_simple_job_dto(return_dto: SimpleJobDto):
    assert return_dto.id == EXPECTED_ID
    assert return_dto.name == STANDARD_JOB_NAME
    assert return_dto.state == JobState.RUNNING


def check_if_job_finished(job: JobDataclass):
    assert job.id == EXPECTED_ID
    assert job.progress == JOB_FINISHED_PROGRESS
    assert job.state == JobState.FINISHED


def ibm_check_if_job_runner_result_correct(job: JobDataclass):
    job.type = JobType.RUNNER
    for i in range(len(job.results)):
        result: ResultDataclass = job.results[i]
        check_standard_result_data(i, job, result)
        assert result.meta_data is not None
        shots: int = job.shots
        if i == 0:
            assert (shots / 2 + RESULT_TOLERANCE) > result.result_dict["0x0"] > (shots / 2 - RESULT_TOLERANCE)
            assert (shots / 2 + RESULT_TOLERANCE) > result.result_dict["0x3"] > (shots / 2 - RESULT_TOLERANCE)
            assert (result.result_dict["0x0"] + result.result_dict["0x3"]) == shots
        else:
            assert result.result_dict["0x0"] == shots


def check_aws_local_simulator_results(results, shots: int):
    for i in range(len(results)):
        results_dict = results[i].result_dict
        counts: Counter = results_dict.get("counts")
        probabilities: dict = results_dict.get("probabilities")
        if i == 0:
            if counts.get("00") is not None and counts.get("11") is not None:
                counts0 = counts.get("00")

                probability00 = probabilities.get("00")
                counts1 = counts.get("11")
                probability11 = probabilities.get("11")
            else:
                raise AssertionError
            assert shots / 2 - RESULT_TOLERANCE < counts0 < shots / 2 + RESULT_TOLERANCE
            assert shots / 2 - RESULT_TOLERANCE < counts1 < shots / 2 + RESULT_TOLERANCE

            assert 0.48 < probability00 < 0.52 and 0.48 < probability11 < 0.52
        else:
            assert counts.get("00") == shots


def check_standard_result_data(i, job, result):
    assert result.result_type == ResultType.get_result_type(job.type)
    assert result.job_id == job.id
    assert result.circuit == job.deployment.programs[i].quantum_circuit
