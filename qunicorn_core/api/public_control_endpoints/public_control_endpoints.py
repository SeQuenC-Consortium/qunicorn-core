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

from flask import jsonify
from flask.views import MethodView

from .root import PUBLIC_CONTROL_API
from ..models.jobs import JobDtoSchema
from ..models.jobs import JobIDSchema


@PUBLIC_CONTROL_API.route("/jobs/")
class JobIDView(MethodView):
    """Jobs endpoint for collection of all jobs."""

    @PUBLIC_CONTROL_API.response(HTTPStatus.OK, JobIDSchema())
    def get(self):
        """Get registered job list."""
        return jsonify("{[\"myDummyJob1\",\"myDummyJob2\"]}"), 200

    @PUBLIC_CONTROL_API.arguments(JobDtoSchema(), location="json")
    @PUBLIC_CONTROL_API.response(HTTPStatus.OK, JobIDSchema())
    def post(self, new_job_data: dict):
        """Create/Register new job."""

        return jsonify({"taskmode": f"Job type ",
                        "JobID": "1234"}), 200


@PUBLIC_CONTROL_API.route("/<string:job_id>/")
class JobDetailView(MethodView):
    """Jobs endpoint for a single job."""

    @PUBLIC_CONTROL_API.response(HTTPStatus.OK, JobIDSchema())
    def get(self, job_id: str):
        """Get the Results by ID"""

        return jsonify({"result": "42"}), 200

    @PUBLIC_CONTROL_API.arguments(JobDtoSchema(), location="json")
    @PUBLIC_CONTROL_API.response(HTTPStatus.OK, JobIDSchema())
    def post(self, job_id: str):
        """Run a job execution via id."""

        return jsonify({"status": "running"}), 200

    @PUBLIC_CONTROL_API.arguments(JobDtoSchema(), location="json")
    @PUBLIC_CONTROL_API.response(HTTPStatus.OK, JobIDSchema())
    def delete(self, job_id: str):
        """Delete job data via id."""

        return jsonify({"status": "deleted"}), 200

    @PUBLIC_CONTROL_API.arguments(JobDtoSchema(), location="json")
    @PUBLIC_CONTROL_API.response(HTTPStatus.OK, JobIDSchema())
    def patch(self, job_id: str):
        """Pause a job via id."""

        return jsonify({"status": "pause"}), 200

    @PUBLIC_CONTROL_API.arguments(JobDtoSchema(), location="json")
    @PUBLIC_CONTROL_API.response(HTTPStatus.OK, JobIDSchema())
    def put(self, job_id: str):
        """cancel a job via id."""

        return jsonify({"status": "canceled"}), 200
