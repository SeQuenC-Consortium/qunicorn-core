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

from .root import USER_API
from ..api_models.user_dtos import UserDtoSchema

from ...core import user_service


@USER_API.route("/")
class UserView(MethodView):
    """Root endpoint of the user api, to list all available user_apis."""

    @USER_API.response(HTTPStatus.OK, UserDtoSchema(many=True))
    def get(self):
        """Get all users from the database"""
        return user_service.get_all_users()


@USER_API.route("/<string:user_id>/")
class UserIdView(MethodView):
    """Users Endpoint to get properties of a specific user via ID."""

    @USER_API.response(HTTPStatus.OK, UserDtoSchema())
    def get(self, user_id):
        """Get information about a single user."""
        return user_service.get_user_by_id(user_id), 200
