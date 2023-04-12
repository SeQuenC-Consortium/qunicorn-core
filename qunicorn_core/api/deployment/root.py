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


"""Module containing the root endpoint of the DEPLOYMENT API."""

from dataclasses import dataclass
from flask.helpers import url_for
from flask.views import MethodView
from http import HTTPStatus
from ..util import SecurityBlueprint as SmorestBlueprint
from ..models import RootSchema


DEPLOYMENT_API = SmorestBlueprint(
    "deployment-api",
    "DEPLOYMENT API",
    description="Deployment API for the control plane.",
    url_prefix="/deployments/",
)


@dataclass()
class RootData:
    root: str
