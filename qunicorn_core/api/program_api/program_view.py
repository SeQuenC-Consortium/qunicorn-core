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


"""Module containing the routes of the devices API."""

from http import HTTPStatus

from flask import jsonify
from flask.views import MethodView

from .root import PROGRAM_API
from ..api_models import QuantumProgramSchema, QuantumProgramDto
from ...core.programmanager import programmanager_service


@PROGRAM_API.route("/")
class QuantumProgramView(MethodView):
    """Quantum program Endpoint to get properties of a specific quantum program."""

    @PROGRAM_API.response(HTTPStatus.OK, QuantumProgramSchema())
    def get(self):
        """Get deployed program definition list."""

        pass

    @PROGRAM_API.arguments(QuantumProgramSchema(), location="json")
    @PROGRAM_API.response(HTTPStatus.OK, QuantumProgramSchema())
    def post(self, body):
        """Create a specific quantum program"""
        program_dto: QuantumProgramDto = QuantumProgramDto(**body)
        program_response_dto = programmanager_service.create_database_program(program_dto)
        return jsonify(program_response_dto), 200
