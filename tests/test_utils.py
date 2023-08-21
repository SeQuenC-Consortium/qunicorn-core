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

from qunicorn_core.api.api_models import DeploymentRequestDto, JobRequestDto, DeploymentDto
from qunicorn_core.core import deployment_service
from qunicorn_core.static.enums.provider_name import ProviderName

JOB_JSON_IBM = "job_request_dto_test_data_IBM.json"
JOB_JSON_AWS = "job_request_dto_test_data_AWS.json"
DEPLOYMENT_JSON = "deployment_request_dto_test_data.json"
DEPLOYMENT_CIRCUITS_JSON_IBM = "deployment_request_dto_with_circuit_test_data_IBM.json"
DEPLOYMENT_CIRCUITS_JSON_AWS = "deployment_request_dto_with_circuit_test_data_AWS.json"
PROGRAM_JSON = "program_request_dto_test_data.json"


def get_object_from_json(json_file_name: str):
    """Returns the json object out of the json file with the name json_file_name"""
    resource_folder: str = "test_resources"

    root_dir = os.path.dirname(os.path.abspath(__file__))
    path_dir = "{}{}{}{}{}".format(root_dir, os.sep, resource_folder, os.sep, json_file_name)
    with open(path_dir) as f:
        data = json.load(f)
    return data


def save_deployment_and_add_id_to_job(job_request_dto: JobRequestDto, provider: ProviderName):
    deployment_request: DeploymentRequestDto = get_test_deployment_request(provider)
    deployment: DeploymentDto = deployment_service.create_deployment(deployment_request)
    job_request_dto.deployment_id = deployment.id


def get_test_deployment_request(provider: ProviderName) -> DeploymentRequestDto:
    if provider == ProviderName.IBM:
        deployment_dict: dict = get_object_from_json(DEPLOYMENT_CIRCUITS_JSON_IBM)
        return DeploymentRequestDto.from_dict(deployment_dict)
    elif provider == ProviderName.AWS:
        deployment_dict: dict = get_object_from_json(DEPLOYMENT_CIRCUITS_JSON_AWS)
        return DeploymentRequestDto.from_dict(deployment_dict)


def get_test_job(provider: ProviderName) -> JobRequestDto:
    if provider == ProviderName.IBM:
        job_dict: dict = get_object_from_json(JOB_JSON_IBM)
        return JobRequestDto(**job_dict)
    elif provider == ProviderName.AWS:
        job_dict: dict = get_object_from_json(JOB_JSON_AWS)
        return JobRequestDto(**job_dict)
