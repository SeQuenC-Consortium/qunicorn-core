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

from dataclasses import dataclass
from http import HTTPStatus

from flask import jsonify
from flask.helpers import url_for
from flask.views import MethodView

from . import jobmanager
from .job_dto import JobDto
from .root import JOBMANAGER_API
from ..models.jobs import JobDtoSchema
from ..models.jobs import JobIDSchema
from ...core.jobmanager import jobmanager_service
from ...db.database_services import database_service, job_service
from ...db.models.job import Job


@dataclass
class JobID:
    id: str
    description: str
    taskmode: int


@JOBMANAGER_API.route("/")
class JobIDView(MethodView):
    """Jobs endpoint for collection of all jobs."""

    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def get(self):
        """Get registered job list."""
        return [
            JobID(
                id=url_for("jobmanager-api.JobIDView", _external=True),
                description="Placeholder for Jobs",
                taskmode=0,
            )
        ]

    @JOBMANAGER_API.arguments(JobDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def post(self, new_job_data):
        """Create/Register and run new job."""
        job_dto: JobDto = JobDto(**new_job_data)
        job = job_service.create_database_job(job_dto)
        job_dto.id = job.id
        # TODO: execute asynchronous (has been that way before)
        job_dict = vars(job_dto)
        jobmanager_service.create_and_run_job.delay(job_dict)
        return jsonify({'job_id': job.id}), 200


@JOBMANAGER_API.route("/<string:job_id>/")
class JobDetailView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.response(HTTPStatus.OK, JobDtoSchema())
    def get(self, job_id: str):
        """Get the urls for the jobmanager api for job control."""
        results = database_service.get_database_object(int(job_id), Job)
        return jsonify({'results': results}), 200

    @JOBMANAGER_API.arguments(JobDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def post(self, job_id: str):
        """Run a job execution via id."""
        jobmanager.run_job()
        pass

    @JOBMANAGER_API.arguments(JobDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def post(self, job_id: str):
        """Cancel a job execution via id."""

        pass

    @JOBMANAGER_API.arguments(JobDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def delete(self, job_id: str):
        """Delete job data via id."""

        pass

    @JOBMANAGER_API.arguments(JobDtoSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def put(self, job_id: str):
        """Pause a job via id."""

        pass
