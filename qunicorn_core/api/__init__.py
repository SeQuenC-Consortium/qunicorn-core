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


"""Module containing all API related code of the project."""

from http import HTTPStatus
from typing import Dict

import marshmallow as ma
from flask import Flask
from flask.helpers import url_for
from flask.views import MethodView
from flask_smorest import Api
from flask_smorest import Blueprint as SmorestBlueprint

from .flask_api_utils import MaBaseSchema

"""A single API instance. All api versions should be blueprints."""
API = Api(spec_kwargs={"title": "QUNICORN_API", "version": "v1"})


class VersionsRootSchema(MaBaseSchema):
    title = ma.fields.String(required=True, allow_none=False, dump_only=True)
    jobs = ma.fields.Url(required=False, allow_none=False, dump_only=True)
    devices = ma.fields.Url(required=False, allow_none=False, dump_only=True)
    deployments = ma.fields.Url(required=False, allow_none=False, dump_only=True)
    provider = ma.fields.Url(required=False, allow_none=False, dump_only=True)
    api_spec = ma.fields.Url(required=False, allow_none=False, dump_only=True)
    swagger_ui = ma.fields.Url(required=False, allow_none=False, dump_only=True)
    rapidoc = ma.fields.Url(required=False, allow_none=False, dump_only=True)
    licenses = ma.fields.Url(required=False, allow_none=False, dump_only=True)


ROOT_ENDPOINT = SmorestBlueprint(
    "api-root",
    "root",
    # url_prefix="/api",
    description="The API endpoint pointing towards all api versions.",
)


@ROOT_ENDPOINT.route("/")
class RootView(MethodView):
    @ROOT_ENDPOINT.response(HTTPStatus.OK, VersionsRootSchema())
    def get(self) -> Dict[str, str]:
        """Get the Root API information containing the links to all versions of this api."""
        return {
            "title": API.spec.title,
            "jobs": url_for("job-api.JobIDView", _external=True),
            "devices": url_for("device-api.DeviceView", _external=True),
            "deployments": url_for("deployment-api.DeploymentIDView", _external=True),
            "provider": url_for("provider-api.ProviderView", _external=True),
            "api_spec": url_for("api-docs.openapi_json", _external=True),
            "swagger_ui": url_for("api-docs.openapi_swagger_ui", _external=True),
            "rapidoc": url_for("api-docs.openapi_rapidoc", _external=True),
            "licenses": url_for("licenses.show_licenses", _external=True),
        }


def register_root_api(app: Flask):
    """Register the API with the flask app."""
    from .deployment_api import DEPLOYMENT_API
    from .device_api import DEVICES_API
    from .job_api import JOBMANAGER_API
    from .jwt import SECURITY_SCHEMES
    from .provider_api import PROVIDER_API

    API.init_app(app)

    # register security schemes in doc
    for name, scheme in SECURITY_SCHEMES.items():
        API.spec.components.security_scheme(name, scheme)

    # register API blueprints (only do this after the API is registered with flask!)
    API.register_blueprint(ROOT_ENDPOINT)
    API.register_blueprint(JOBMANAGER_API)
    API.register_blueprint(DEVICES_API)
    API.register_blueprint(DEPLOYMENT_API)
    API.register_blueprint(PROVIDER_API)
