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

from typing import Dict
from flask import Flask
from flask.helpers import url_for
from flask.views import MethodView
import marshmallow as ma
from flask_smorest import Api, Blueprint as SmorestBlueprint
from http import HTTPStatus
from .util import MaBaseSchema
from .jobmanager import JOBMANAGER_API
from .devices import DEVICES_API
from .deployment import DEPLOYMENT_API
from .services import SERVICES_API
from .usermanager import USERS_API
from .jwt import SECURITY_SCHEMES


"""A single API instance. All api versions should be blueprints."""
API = Api(spec_kwargs={"title": "QUNICORN_API", "version": "v1"})


class VersionsRootSchema(MaBaseSchema):
    title = ma.fields.String(required=True, allow_none=False, dump_only=True)
    v1 = ma.fields.Url(required=False, allow_none=False, dump_only=True)


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
            "v1": url_for("jobmanager-api.JobIDView", _external=True),
            # "v1": url_for("devices-api.DeviceView", _external=True),
        }


def register_root_api(app: Flask):
    """Register the API with the flask app."""
    API.init_app(app)

    # register security schemes in doc
    for name, scheme in SECURITY_SCHEMES.items():
        API.spec.components.security_scheme(name, scheme)

    # register API blueprints (only do this after the API is registered with flask!)
    API.register_blueprint(ROOT_ENDPOINT)
    API.register_blueprint(JOBMANAGER_API)
    API.register_blueprint(DEVICES_API)
    API.register_blueprint(DEPLOYMENT_API)
    API.register_blueprint(SERVICES_API)
    API.register_blueprint(USERS_API)
