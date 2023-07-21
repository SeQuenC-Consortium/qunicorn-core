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

from flask.views import MethodView

from .root import DEPLOYMENT_API
from ..api_models.deployment_dtos import DeploymentDtoSchema, DeploymentRequestDtoSchema, DeploymentRequestDto
from ...core.jobmanager import deployment_service


@DEPLOYMENT_API.route("/")
class DeploymentIDView(MethodView):
    """Deployments endpoint for collection of all deployed jobs."""

    @DEPLOYMENT_API.response(HTTPStatus.OK)
    def get(self):
        """Get the list of deployments."""
        return deployment_service.get_all_deployments()

    @DEPLOYMENT_API.arguments(DeploymentRequestDtoSchema(), location="json")
    @DEPLOYMENT_API.response(HTTPStatus.CREATED, DeploymentDtoSchema())
    def post(self, body):
        """Create/Deploy new Job-definition."""
        deployment_dto: DeploymentRequestDto = DeploymentRequestDto.from_dict(body)
        return deployment_service.create_deployment(deployment_dto)


@DEPLOYMENT_API.route("/<string:deployment_id>/")
class DeploymentDetailView(MethodView):
    """API endpoint for single pre-deployments."""

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def get(self, deployment_id: int):
        """Get detailed information for single deployed job-definition."""

        return deployment_service.get_deployment(deployment_id)

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def delete(self, deployment_id: int):
        """TBD: Delete single deployment by ID."""
        raise NotImplementedError
        # Otherwise it would return an integrity error
        return deployment_service.delete_deployment(deployment_id)

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    @DEPLOYMENT_API.arguments(DeploymentRequestDtoSchema(), location="json")
    def put(self, body, deployment_id: int):
        """TBD: Update single deployment by ID."""
        raise NotImplementedError
        # Otherwise it would return an integrity error
        deployment_dto: DeploymentRequestDto = DeploymentRequestDto.from_dict(body)
        return deployment_service.update_deployment(deployment_dto, deployment_id)

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def patch(self, deployment_id: int):
        """TBD: Update parts of a single deployment by ID."""

        raise NotImplementedError


@DEPLOYMENT_API.route("/<string:deployment_id>/jobs")
class DeploymentDetailJobView(MethodView):
    """API endpoint for running jobs of a single deployment."""

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def get(self, deployment_id: str):
        """TBD: Get job definitions of a single deployment."""

        raise NotImplementedError
