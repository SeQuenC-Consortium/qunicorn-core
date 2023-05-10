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

from qunicorn_core.celery import CELERY
from ..models.jobs import JobIDSchema
from ..models.jobs import JobRegisterSchema
from typing import Dict
from flask.helpers import url_for
from flask.views import MethodView
from flask import request, jsonify
from dataclasses import dataclass
from http import HTTPStatus
from .job_pilots import QiskitPilot, AWSPilot
import time

from .root import JOBMANAGER_API


@dataclass
class JobID:
    id: str
    description: str
    taskmode: int


@dataclass
class JobRegister:
    circuit: str
    provider: str
    qpu: str
    credentials: dict
    shots: int
    circuit_format: str


qiskitpilot = QiskitPilot
awspilot = AWSPilot


@CELERY.task()
def createJob(request):
    """Create a job and assign to the target pilot"""
    if request == "IBMQ":
        pilot = qiskitpilot("QP")
        pilot.execute("123456")
        print(f"Job Registered at {request}")
        time.sleep(5)
        print("Job complete")
    else:
        print("No valid target specified")
    return 0


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

    @JOBMANAGER_API.arguments(JobRegisterSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def post(self, new_job_data: dict):
        """Create/Register new job."""

        request_data = request.get_json()
        target = request_data["target"]
        print(target)
        createJob.delay(target)
        return jsonify({"taskmode": f"Job type {target}"}), 200


@JOBMANAGER_API.route("/<string:job_id>/")
class JobDetailView(MethodView):
    """Jobs endpoint for a single job."""

    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def get(self, job_id: str):
        """Get the urls for the jobmanager api for job control."""

        pass

    @JOBMANAGER_API.arguments(JobRegisterSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def post(self, job_id: str):
        """Cancel a job execution via id."""

        pass

    @JOBMANAGER_API.arguments(JobRegisterSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def delete(self, job_id: str):
        """Delete job data via id."""

        pass

    @JOBMANAGER_API.arguments(JobRegisterSchema(), location="json")
    @JOBMANAGER_API.response(HTTPStatus.OK, JobIDSchema())
    def put(self, job_id: str):
        """Pause a job via id."""

        pass
