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


"""Module containing the routes of the Taskmanager API."""
from http import HTTPStatus

from flask.views import MethodView

from .root import PROVIDER_API
from ..api_models.provider_dtos import ProviderDtoSchema, ProviderIDSchema


@PROVIDER_API.route("/<string:service_id>/")
class ProviderView(MethodView):
    """Services Endpoint to get properties of a specific service."""

    @PROVIDER_API.arguments(ProviderIDSchema(), location="path")
    @PROVIDER_API.response(HTTPStatus.OK, ProviderDtoSchema())
    def get(self):
        """Get information about a single service."""

        pass
