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

"""pytest utils file"""
import json
import os
from typing import Optional

from qunicorn_core.api.api_models import (
    DeploymentUpdateDto,
    JobRequestDto,
    JobRequestDtoSchema,
    SimpleJobDto,
    DeploymentDto,
)
from qunicorn_core.core import deployment_service, job_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.static.qunicorn_exception import QunicornError
from tests.conftest import set_up_env

# The ProviderName must be in lower case in the file name
JOB_JSON_PATHS = [
    "job_request_dto_ibm_test_data.json",
    "job_request_dto_aws_test_data.json",
    "job_request_dto_qunicorn_test_data.json",
    "job_request_dto_rigetti_test_data.json",
]

# The AssemblerLanguage must be in lower case in the file name
DEPLOYMENT_JSON_PATHS = [
    "deployment_request_dto_qasm2_test_data.json",
    "deployment_request_dto_qasm3_test_data.json",
    "deployment_request_dto_braket_test_data.json",
    "deployment_request_dto_qiskit_test_data.json",
    "deployment_request_dto_qrisp_test_data.json",
    "deployment_request_dto_qunicorn_test_data.json",
    "deployment_request_dto_quil_test_data.json",
]

AWS_LOCAL_SIMULATOR = "local_simulator"
IBM_LOCAL_SIMULATOR = "aer_simulator"
EXPECTED_ID: int = 5  # hardcoded ID can be removed if tests for the correct ID are no longer needed
JOB_FINISHED_PROGRESS: int = 100
STANDARD_JOB_NAME: str = "JobName"
IS_ASYNCHRONOUS: bool = False
COUNTS_TOLERANCE: int = 200
PROBABILITY_1: float = 1
PROBABILITY_TOLERANCE: float = 0.1
BIT_0: str = "0x0"
BIT_1: str = "0x1"
BIT_3: str = "0x3"
BIT_8: str = "0x7"


def execute_job_test(
    provider: ProviderName,
    device: str,
    assembler_language_list: list[AssemblerLanguage],
    is_asynchronous: bool = False,
):
    """
    This is the main testing method to test the execution of a job on a device of a provider.
    To use this method you need a program with two circuits, which are logically equivalent to the others.
    Eg: deployment_request_dto_qiskit_test_data.json

    It is an End-to-End test, which means that the job is created and executed on the provider.
    Afterward it is checked if the job is saved in the database and if the results are correct.
    This can be done for different assembler languages and providers.
    """

    # GIVEN: Database Setup
    app = set_up_env()

    with app.app_context():
        job_request_dto: JobRequestDto = get_test_job(provider)
        job_request_dto.device_name = device
        save_deployment_and_add_id_to_job(job_request_dto, assembler_language_list)

        # WHEN: create_and_run
        return_dto: SimpleJobDto = job_service.create_and_run_job(job_request_dto, is_asynchronous)

        # THEN: Check if the correct job with its result is saved in the db with results with a RESULT_TOLERANCE
        check_simple_job_dto(return_dto)
        job: JobDataclass = JobDataclass.get_by_id_or_404(return_dto.id)
        check_if_job_finished(job)
        check_if_job_runner_result_correct(job)


def get_object_from_json(json_file_name: str):
    """Returns the json object out of the json file with the name json_file_name"""
    resource_folder: str = "test_resources"

    root_dir = os.path.dirname(os.path.abspath(__file__))
    path_dir = "{}{}{}{}{}".format(root_dir, os.sep, resource_folder, os.sep, json_file_name)
    with open(path_dir) as f:
        data = json.load(f)
    return data


def save_deployment_and_add_id_to_job(job_request_dto: JobRequestDto, assembler_language_list: list[AssemblerLanguage]):
    """Save the deployment and add the id to the job_request_dto"""
    deployment_request: DeploymentUpdateDto = get_test_deployment_request(
        assembler_language_list=assembler_language_list
    )
    deployment: DeploymentDto = deployment_service.create_deployment(deployment_request)
    job_request_dto.deployment_id = deployment.id


def get_test_deployment_request(assembler_language_list: list[AssemblerLanguage]) -> DeploymentUpdateDto:
    """Search for an assembler_language in the file names to create a DeploymentRequestDto"""
    deployment_dict: Optional[dict] = None
    combined_deployment_dict_programs = []
    for path in DEPLOYMENT_JSON_PATHS:
        for assembler_language in assembler_language_list:
            if assembler_language.lower() in path:
                # Filling Deployment Dict from path for correct assembler language
                deployment_dict = get_object_from_json(path)
                # Extend programs with programs from other assembler languages
                combined_deployment_dict_programs.extend(deployment_dict["programs"])
    if len(combined_deployment_dict_programs) > 0:
        # Return DeploymentDict as DeploymentRequestDto with all combined programs
        deployment_dict["programs"] = combined_deployment_dict_programs
        return DeploymentUpdateDto.from_dict(deployment_dict)
    else:
        # Raise Error if no deployment json was found
        raise QunicornError("No deployment json found for assembler_language: {}".format(assembler_language_list))


def get_test_job(provider: ProviderName) -> JobRequestDto:
    """Search for a ProviderName in the file names to create a JobRequestDto"""
    for path in JOB_JSON_PATHS:
        if provider.lower() in path:
            job_dict: dict = JobRequestDtoSchema().load(get_object_from_json(path))
            return JobRequestDto(**job_dict)

    raise QunicornError("No job json found for provider: {}".format(provider))


def check_simple_job_dto(return_dto: SimpleJobDto):
    assert return_dto.id == EXPECTED_ID
    assert return_dto.name == STANDARD_JOB_NAME
    assert return_dto.state == JobState.READY


def check_if_job_finished(job: JobDataclass):
    assert job.id == EXPECTED_ID
    assert job.state == JobState.FINISHED
    assert job.progress == JOB_FINISHED_PROGRESS


def check_if_job_runner_result_correct(job: JobDataclass):
    """Iterate over every result and check if the distribution of the measurement is correct"""
    program_id_to_index = {program.id: i for i, program in enumerate(job.deployment.programs)}
    check_job_data(job)

    for result_index in range(len(job.results)):
        result: ResultDataclass = job.results[result_index]
        program_index = program_id_to_index[result.program_id]

        shots: int = job.shots
        data: dict = result.data

        if program_index == 0:
            # Check if the first result is distributed correctly: 50% for the qubit zero and 50% for the qubit three
            if result.result_type == ResultType.COUNTS:
                assert compare_values_with_tolerance(shots / 2, data[BIT_0], COUNTS_TOLERANCE)
                assert compare_values_with_tolerance(shots / 2, data[BIT_3], COUNTS_TOLERANCE)
                assert (data[BIT_0] + data[BIT_3]) == shots

            if result.result_type == ResultType.PROBABILITIES:
                assert compare_values_with_tolerance(PROBABILITY_1 / 2, data[BIT_0], PROBABILITY_TOLERANCE)
                assert compare_values_with_tolerance(PROBABILITY_1 / 2, data[BIT_3], PROBABILITY_TOLERANCE)
                assert (data[BIT_0] + data[BIT_3]) > PROBABILITY_1 - PROBABILITY_TOLERANCE

        if program_index == 1:
            # Check if the first result is distributed correctly: 100% for the qubit zero
            if result.result_type == ResultType.COUNTS:
                assert data[BIT_0] == shots

            if result.result_type == ResultType.PROBABILITIES:
                assert data[BIT_0] == PROBABILITY_1


def compare_values_with_tolerance(value1, value2, tolerance) -> bool:
    return value1 + tolerance > value2 > value1 - tolerance


def check_job_data(job: JobDataclass):
    program_ids_from_results = {result.program_id for result in job.results}
    program_ids_from_deployment = {program.id for program in job.deployment.programs}

    assert program_ids_from_results == program_ids_from_deployment  # every program needs at least one result

    result: ResultDataclass

    for result in job.results:
        assert result.result_type != ResultType.ERROR, result
        assert result.job_id == job.id
        check_standard_result_data(job, result)


def check_standard_result_data(job: JobDataclass, result: ResultDataclass):
    assert result.result_type != ResultType.ERROR, result
    assert result.job_id == job.id

    program_ids = {program.id for program in job.deployment.programs}

    assert result.program_id in program_ids


def check_if_job_runner_result_correct_multiple_gates(job: JobDataclass):
    """Iterate over every result and check if the distribution of the measurement is correct"""
    program_id_to_index = {program.id: i for i, program in enumerate(job.deployment.programs)}
    check_job_data(job)

    for result_index in range(len(job.results)):
        result: ResultDataclass = job.results[result_index]
        program_index = program_id_to_index[result.program_id]

        shots: int = job.shots
        result_data: dict = result.data
        prob_tolerance: float = PROBABILITY_TOLERANCE * 2
        count_tolerance: float = COUNTS_TOLERANCE * 2

        if program_index in [0, 1, 3, 4]:
            qubit = BIT_8 if program_index == 3 else BIT_1

            if result.result_type == ResultType.COUNTS:
                assert result_data[qubit] == shots

            if result.result_type == ResultType.PROBABILITIES:
                assert result_data[qubit] == PROBABILITY_1

        if program_index == 2:
            if result.result_type == ResultType.COUNTS:
                assert compare_values_with_tolerance(7 * (shots / 8), result_data[BIT_0], count_tolerance)
                assert compare_values_with_tolerance(shots / 8, result_data[BIT_1], count_tolerance)
                assert (result_data[BIT_0] + result_data[BIT_1]) == shots

            if result.result_type == ResultType.PROBABILITIES:
                assert compare_values_with_tolerance(7 * (PROBABILITY_1 / 8), result_data[BIT_0], prob_tolerance)
                assert compare_values_with_tolerance(PROBABILITY_1 / 8, result_data[BIT_1], prob_tolerance)
                assert (result_data[BIT_0] + result_data[BIT_1]) > PROBABILITY_1 - PROBABILITY_TOLERANCE
