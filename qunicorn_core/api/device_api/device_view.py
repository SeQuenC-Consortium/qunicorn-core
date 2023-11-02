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

from flask import jsonify
from flask.views import MethodView

from .root import DEVICES_API
from ..api_models.device_dtos import (
    DeviceDtoSchema,
    DeviceRequestDtoSchema,
    DeviceRequestDto,
    SimpleDeviceDtoSchema,
)
from ...core import device_service
from ...util import logging


@DEVICES_API.route("/")
class DeviceView(MethodView):
    """Root endpoint of the device api, to list all available device_api."""

    @DEVICES_API.arguments(DeviceRequestDtoSchema(), location="json")
    @DEVICES_API.response(HTTPStatus.OK, SimpleDeviceDtoSchema(many=True))
    def put(self, device_request_data):
        """Update the devices by retrieving data from the provider and returning the updated devices."""
        logging.info("Request: update the devices")
        device_request: DeviceRequestDto = DeviceRequestDto(**device_request_data)
        return device_service.update_devices(device_request)

    @DEVICES_API.response(HTTPStatus.OK, SimpleDeviceDtoSchema(many=True))
    def get(self):
        """Get all devices from the database, for more details get the device by id."""
        logging.info("Request: get all devices that are in the database")
        return device_service.get_all_devices()


@DEVICES_API.route("/<string:device_id>/")
class DeviceIdView(MethodView):
    """Devices endpoint to get properties of a specific device."""

    @DEVICES_API.response(HTTPStatus.OK, DeviceDtoSchema())
    def get(self, device_id):
        """Get information about a specific device."""
        logging.info(f"Request: get information about device with id:{device_id}")
        return device_service.get_device_by_id(device_id)


@DEVICES_API.route("/<string:device_id>/status")
class DevicesStatusStatus(MethodView):
    """Devices endpoint to get properties of a specific device."""

    @DEVICES_API.arguments(DeviceRequestDtoSchema(), location="json")
    @DEVICES_API.response(HTTPStatus.OK)
    def post(self, device_request_data, device_id):
        """To check if a specific device is available."""
        logging.info(f"Request: get availability information of the device with id:{device_id}")
        device_request: DeviceRequestDto = DeviceRequestDto(**device_request_data)
        return device_service.check_if_device_available(device_id, device_request.token)


@DEVICES_API.route("/<string:device_id>/calibration")
class DevicesCalibrationView(MethodView):
    """Devices endpoint to get properties of a specific device."""

    @DEVICES_API.arguments(DeviceRequestDtoSchema(), location="json")
    @DEVICES_API.response(HTTPStatus.OK)
    def post(self, device_request_data, device_id):
        """Get configuration data for a specific device in a uniform way."""
        logging.info(f"Request: get configuration data for device with id:{device_id}")
        device_request: DeviceRequestDto = DeviceRequestDto(**device_request_data)
        device = device_service.get_device_data_from_provider(device_id, device_request.token)

        return jsonify(device)
