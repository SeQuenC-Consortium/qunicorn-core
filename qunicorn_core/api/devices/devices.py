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

from ..models.devices import DevicesSchema, DeviceIDSchema
from typing import Dict, List
from flask.helpers import url_for
from flask.views import MethodView
from dataclasses import dataclass
from http import HTTPStatus

from .root import DEVICES_API


@dataclass
class DEVICES:
    serviceType: str
    description: str
    address: str
    status: str
    name: str
    url: str
    simulator: bool


@DEVICES_API.route("/<string:device_id>/")
class DevicesView(MethodView):
    """Devices Endpoint to get properties of a specific device."""

    @DEVICES_API.arguments(DeviceIDSchema(), location="path")
    @DEVICES_API.response(HTTPStatus.OK, DevicesSchema())
    def get(self):
        """Get information about a specific device."""

        pass


@DEVICES_API.route("/<string:device_id>/status")
class DevicesView(MethodView):
    """Devices Endpoint to get properties of a specific device."""

    @DEVICES_API.arguments(DeviceIDSchema(), location="path")
    @DEVICES_API.response(HTTPStatus.OK, DevicesSchema())
    def get(self):
        """Get the status of a specific device."""

        pass


@DEVICES_API.route("/<string:device_id>/calibration")
class DevicesView(MethodView):
    """Devices Endpoint to get properties of a specific device."""

    @DEVICES_API.arguments(DeviceIDSchema(), location="path")
    @DEVICES_API.response(HTTPStatus.OK, DevicesSchema())
    def get(self):
        """Get calibration data for a specific device in a uniform way."""

        pass


@DEVICES_API.route("/<string:device_id>/jobs")
class DevicesView(MethodView):
    """Devices Endpoint to get properties of a specific device/service."""

    @DEVICES_API.response(HTTPStatus.OK, DevicesSchema())
    def get(self):
        """Get the active jobs of a device."""

        pass
