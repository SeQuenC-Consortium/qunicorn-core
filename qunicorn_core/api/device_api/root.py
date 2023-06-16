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


"""Module containing the root endpoint of the DEVICES API."""

from dataclasses import dataclass
from http import HTTPStatus

from flask.helpers import url_for
from flask.views import MethodView

from ..api_models import RootSchema
from ..util import SecurityBlueprint as SmorestBlueprint

DEVICES_API = SmorestBlueprint(
    "device-api",
    "DEVICES API",
    description="Devices API to list available resources.",
    url_prefix="/device_api",
)


@dataclass()
class RootData:
    root: str


@DEVICES_API.route("/")
class RootView(MethodView):
    """Root endpoint of the device api, to list all available device_api."""

    @DEVICES_API.response(HTTPStatus.OK, RootSchema())
    def get(self):
        """Get the urls of the next endpoints of the device_api api to call."""
        return RootData(root=url_for("device-api.DevicesView", _external=True))
