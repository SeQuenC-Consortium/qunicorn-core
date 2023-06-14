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


from http import HTTPStatus

from flask.views import MethodView

from .root import PILOT_MANAGER_API
from ..models.jobs import JobIDSchema


@PILOT_MANAGER_API.route("/")
class JobIDView(MethodView):
    """Jobs endpoint for collection of all jobs."""

    @PILOT_MANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def get(self):
        """Get status of the execution of the pilot."""
        return "OK", 200

    @PILOT_MANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def post(self):
        """Set Pilot state <BLOCKED>/<READY>"""
        return "OK", 200
