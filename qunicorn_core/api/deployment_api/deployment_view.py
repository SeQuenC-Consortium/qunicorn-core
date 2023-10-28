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


"""Module containing the routes of the deployments API."""

from http import HTTPStatus
from typing import Optional

from flask import jsonify
from flask.views import MethodView

from .root import DEPLOYMENT_API
from ..api_models import JobResponseDtoSchema
from ..api_models.deployment_dtos import DeploymentDtoSchema, DeploymentRequestDtoSchema, DeploymentRequestDto
from ...core import deployment_service, job_service
from ...util import logging


@DEPLOYMENT_API.route("/")
class DeploymentIDView(MethodView):
    """Deployments endpoint for collection of all deployed jobs."""

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema(many=True))
    @DEPLOYMENT_API.require_jwt(optional=True)
    def get(self, jwt_subject: Optional[str]):
        """Get the list of deployments."""
        logging.info("Request: get all deployments")
        return deployment_service.get_all_deployments(user_id=jwt_subject)

    @DEPLOYMENT_API.arguments(DeploymentRequestDtoSchema(), location="json")
    @DEPLOYMENT_API.response(HTTPStatus.CREATED, DeploymentDtoSchema())
    @DEPLOYMENT_API.require_jwt(optional=True)
    def post(self, body, jwt_subject: Optional[str]):
        """Create/Deploy new Job-definition."""
        logging.info("Request: create new deployment")
        deployment_dto: DeploymentRequestDto = DeploymentRequestDto.from_dict(body)
        return deployment_service.create_deployment(deployment_dto, user_id=jwt_subject)


@DEPLOYMENT_API.route("/<string:deployment_id>/")
class DeploymentDetailView(MethodView):
    """API endpoint for single pre-deployments."""

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    @DEPLOYMENT_API.require_jwt(optional=True)
    def get(self, deployment_id: int, jwt_subject: Optional[str]):
        """Get detailed information for single deployed job-definition."""
        logging.info("Request: get deployment by id")
        return deployment_service.get_deployment_by_id(deployment_id, jwt_subject)

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    @DEPLOYMENT_API.require_jwt(optional=True)
    def delete(self, deployment_id: int, jwt_subject: Optional[str]):
        """Delete single deployment by ID."""
        logging.info("Request: delete deployment by id")
        return deployment_service.delete_deployment(deployment_id, user_id=jwt_subject)

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    @DEPLOYMENT_API.arguments(DeploymentRequestDtoSchema(), location="json")
    @DEPLOYMENT_API.require_jwt(optional=True)
    def put(self, body, deployment_id: int, jwt_subject: Optional[str]):
        """Update single deployment by ID."""
        logging.info("Request: update deployment by id")
        deployment_dto: DeploymentRequestDto = DeploymentRequestDto.from_dict(body)
        return deployment_service.update_deployment(deployment_dto, deployment_id, user_id=jwt_subject)


@DEPLOYMENT_API.route("/<string:deployment_id>/jobs")
class JobsByDeploymentView(MethodView):
    """API endpoint for jobs of a specific deployment."""

    @DEPLOYMENT_API.response(HTTPStatus.OK, JobResponseDtoSchema(many=True))
    @DEPLOYMENT_API.require_jwt(optional=True)
    def get(self, deployment_id: str, jwt_subject: Optional[str]):
        """Get the details of all jobs with a specific deployment id."""
        logging.info("Request: get jobs with deployment id")
        jobs_by_deployment_id = job_service.get_jobs_by_deployment_id(deployment_id, jwt_subject)
        return (
            jobs_by_deployment_id
            if jobs_by_deployment_id is []
            else jsonify({"Warning": "No Jobs can be found for this DeploymentID"})
        )

    @DEPLOYMENT_API.response(HTTPStatus.OK, JobResponseDtoSchema(many=True))
    @DEPLOYMENT_API.require_jwt(optional=True)
    def delete(self, deployment_id: str, jwt_subject: Optional[str]):
        """Delete all jobs with a specific deployment id."""
        logging.info("Request: delete jobs with deployment id")
        jobs_by_deployment_id = job_service.delete_jobs_by_deployment_id(deployment_id, user_id=jwt_subject)
        return (
            jobs_by_deployment_id
            if jobs_by_deployment_id is []
            else jsonify({"Warning": "No Jobs can be found for this DeploymentID"})
        )
