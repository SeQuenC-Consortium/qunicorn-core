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

from flask import jsonify
from flask.helpers import url_for
from flask.views import MethodView

from .root import JOBMANAGER_API
from ..api_models.job_dtos import (
    JobRequestDtoSchema,
    JobResponseDtoSchema,
    JobRequestDto,
    SimpleJobDto,
    JobResponseDto,
    SimpleJobDtoSchema,
)
from ...core.jobmanager import jobmanager_service
from ...util import logging


@JOBMANAGER_API.route("/")
class JobIDView(MethodView):
    """Jobs endpoint for collection of all jobs."""

    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema())
    def get(self):
        """Get registered job list."""
        jobmanager_service.get_all_jobs()
        return [
            SimpleJobDto(
                id=url_for("job-api.JobIDView", _external=True),
                name="Placeholder for Jobs",
            )
        ]

    @JOBMANAGER_API.arguments(JobRequestDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.CREATED, SimpleJobDtoSchema())
    def post(self, body):
        """Create/Register and run new job."""
        job_dto: JobRequestDto = JobRequestDto(**body)
        job_id: SimpleJobDto = jobmanager_service.create_and_run_job(job_dto)
        return jsonify(job_id), 200


@JOBMANAGER_API.route("/<string:job_id>/")
class JobDetailView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.response(HTTPStatus.OK, JobResponseDtoSchema())
    def get(self, job_id: str):
        """Get the details/results of a job."""
        job_response_dto: JobResponseDto = jobmanager_service.get_job(int(job_id))
        return jsonify(job_response_dto), 200

    @JOBMANAGER_API.arguments(JobRequestDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema())
    def delete(self, body, job_id: str):
        """Delete job data via id."""

        return jsonify(jobmanager_service.delete_job_data_by_id(job_id))


@JOBMANAGER_API.route("/run/<string:job_id>/")
class JobRunView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.arguments(JobRequestDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema())
    def post(self, body, job_id: str):
        """Run a job execution via id. tbd"""
        logging.info("Request: run job")
        return jsonify(jobmanager_service.run_job_by_id(int(job_id))), 200


@JOBMANAGER_API.route("/cancel/<string:job_id>/")
class JobCancelView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.arguments(JobRequestDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema())
    def post(self, body, job_id: str):
        """Cancel a job execution via id."""
        logging.info("Request: cancel job")

        return jsonify(jobmanager_service.cancel_job_by_id(job_id)), 200


@JOBMANAGER_API.route("/pause/<string:job_id>/")
class JobPauseView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.arguments(JobRequestDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, SimpleJobDtoSchema())
    def post(self, body, job_id: str):
        """Pause a job via id."""
        logging.info("Request: pause job")

        return jsonify(jobmanager_service.pause_job_by_id(job_id)), 200
