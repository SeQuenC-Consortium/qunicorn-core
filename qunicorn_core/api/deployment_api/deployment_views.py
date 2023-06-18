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
from ..api_models.deployment_dtos import DeploymentDtoSchema


@DEPLOYMENT_API.route("/")
class DeploymentIDView(MethodView):
    """Deployments endpoint for collection of all deployed jobs."""

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema())
    def get(self):
        """Get pre-deployed job definition list."""

        pass

    @DEPLOYMENT_API.arguments(DeploymentDtoSchema(), location="json")
    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema())
    def post(self, new_task_data: dict):
        """Deploy new Job-definition."""

        pass


@DEPLOYMENT_API.route("/<string:deployment_id>/")
class DeploymentDetailView(MethodView):
    """API endpoint for single pre-deployments."""

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def get(self, deployment_id: str):
        """Get detailed information for single pre-deployed job-definitions."""

        pass

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def delete(self, deployment_id: str):
        """Delete single pre-deployment_api."""

        pass

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def put(self):
        """Update single pre-deployment_api."""

        pass

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def patch(self):
        """Update parts of a single pre-deployment_api."""

        pass


@DEPLOYMENT_API.route("/<string:deployment_id>/jobs")
class DeploymentDetailJobView(MethodView):
    """API endpoint for running jobs of a single pre-deployment_api."""

    @DEPLOYMENT_API.response(HTTPStatus.OK, DeploymentDtoSchema)
    def get(self, deployment_id: str):
        """Get job definitions of a single pre-deployment_api."""

        pass