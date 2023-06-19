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

from flask.views import MethodView

from .root import DEVICES_API
from ..api_models.device_dtos import DevicesDtoSchema, DeviceIDSchema


@DEVICES_API.route("/<string:device_id>/")
class DeviceView(MethodView):
    """Devices Endpoint to get properties of a specific device."""

    @DEVICES_API.arguments(DeviceIDSchema(), location="path")
    @DEVICES_API.response(HTTPStatus.OK, DevicesDtoSchema())
    def get(self):
        """Get information about a specific device."""

        pass


@DEVICES_API.route("/<string:device_id>/status")
class DevicesStatusStatus(MethodView):
    """Devices Endpoint to get properties of a specific device."""

    @DEVICES_API.arguments(DeviceIDSchema(), location="path")
    @DEVICES_API.response(HTTPStatus.OK, DevicesDtoSchema())
    def get(self):
        """Get the status of a specific device."""

        pass


@DEVICES_API.route("/<string:device_id>/calibration")
class DevicesCalibrationView(MethodView):
    """Devices Endpoint to get properties of a specific device."""

    @DEVICES_API.arguments(DeviceIDSchema(), location="path")
    @DEVICES_API.response(HTTPStatus.OK, DevicesDtoSchema())
    def get(self):
        """Get calibration data for a specific device in a uniform way."""

        pass


@DEVICES_API.route("/<string:device_id>/jobs")
class DevicesJobsView(MethodView):
    """Devices Endpoint to get properties of a specific device/service."""

    @DEVICES_API.response(HTTPStatus.OK, DevicesDtoSchema())
    def get(self):
        """Get the active jobs of a device."""

        pass
