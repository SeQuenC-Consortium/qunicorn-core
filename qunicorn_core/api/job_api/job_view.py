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


"""Module containing the routes of the job manager API."""
from http import HTTPStatus
from typing import Optional

from flask import jsonify
from flask.views import MethodView
from qiskit_ibm_runtime.exceptions import RuntimeInvalidStateError
from qiskit_ibm_runtime.exceptions import IBMRuntimeError

from qunicorn_core.static.qunicorn_exception import QunicornError


from .root import JOBMANAGER_API
from ..api_models.job_dtos import (
    JobRequestDtoSchema,
    JobResponseDtoSchema,
    JobRequestDto,
    JobResponseDto,
    TokenSchema,
    SimpleJobDtoSchema,
    JobExecutionDtoSchema,
    JobExecutePythonFileDto,
    SimpleJobDto,
)
from ..jwt import abort_if_user_unauthorized
from ...core import job_service
from ...util import logging


@JOBMANAGER_API.route("/")
class JobIDView(MethodView):
    """Jobs endpoint for collection of all jobs."""

    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema(many=True))
    @JOBMANAGER_API.require_jwt(optional=True)
    def get(self, jwt_subject: Optional[str]):
        """Get all created jobs."""

        return jsonify(job_service.get_all_jobs(user_id=jwt_subject))

    @JOBMANAGER_API.arguments(JobRequestDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.CREATED, SimpleJobDtoSchema())
    @JOBMANAGER_API.require_jwt(optional=True)
    def post(self, body, jwt_subject: Optional[str]):
        """Create/Register and run new job."""
        job_dto: JobRequestDto = JobRequestDto(**body)
        job_response: SimpleJobDto = job_service.create_and_run_job(job_dto, user_id=jwt_subject)
        return jsonify(job_response)


@JOBMANAGER_API.route("/<string:job_id>/")
class JobDetailView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.response(HTTPStatus.OK, JobResponseDtoSchema())
    @JOBMANAGER_API.require_jwt(optional=True)
    def get(self, job_id: str, jwt_subject: Optional[str]):
        """Get the details/results of a job."""
        job_response_dto: JobResponseDto = job_service.get_job_by_id(int(job_id))
        abort_if_user_unauthorized(job_response_dto.executed_by, jwt_subject)
        return jsonify(job_response_dto), 200

    @JOBMANAGER_API.response(HTTPStatus.OK, JobResponseDtoSchema())
    @JOBMANAGER_API.require_jwt(optional=True)
    def delete(self, job_id: str, jwt_subject: Optional[str]):
        """Delete job data via id and return the deleted job."""
        return job_service.delete_job_data_by_id(job_id, user_id=jwt_subject)


@JOBMANAGER_API.route("/run/<string:job_id>/")
class JobRunView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.arguments(JobExecutionDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema())
    @JOBMANAGER_API.require_jwt(optional=True)
    def post(self, body, job_id: int, jwt_subject: Optional[str]):
        """Run job on IBM that was previously Uploaded."""
        logging.info("Request: run job")
        job_execution_dto: JobExecutePythonFileDto = JobExecutePythonFileDto(**body)
        return jsonify(job_service.run_job_by_id(int(job_id), job_execution_dto, user_id=jwt_subject)), 200


@JOBMANAGER_API.route("/rerun/<string:job_id>/")
class JobReRunView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.arguments(TokenSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema())
    @JOBMANAGER_API.require_jwt(optional=True)
    def post(self, body, job_id: int, jwt_subject: Optional[str]):
        """Create a new job on basis of an existing job and execute it."""
        logging.info("Request: re run job")
        return jsonify(job_service.re_run_job_by_id(job_id, body["token"], user_id=jwt_subject))


@JOBMANAGER_API.route("/cancel/<string:job_id>/")
class JobCancelView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.arguments(TokenSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema())
    @JOBMANAGER_API.require_jwt(optional=True)
    def post(self, body, job_id: str, jwt_subject: Optional[str]):
        """Cancel a job execution via id."""
        logging.info("Request: cancel job")
        return jsonify(job_service.cancel_job_by_id(job_id, body["token"], user_id=jwt_subject)), 200
