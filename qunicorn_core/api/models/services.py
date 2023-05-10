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


"""Module containing all API schemas for tasks in the Services API."""

import marshmallow as ma
from ..util import MaBaseSchema

__all__ = ["ServicesSchema", "ServiceIDSchema"]


class ServicesSchema(MaBaseSchema):
    service_id = ma.fields.String(required=True, allow_none=False)
    service_type = ma.fields.String(required=True, allow_none=False)
    provider_name = ma.fields.String(required=True, allow_none=False)
    status = ma.fields.String(required=True, allow_none=False)
    description = ma.fields.String(required=True, allow_none=False)
    url = ma.fields.String(required=True, allow_none=False)


class ServiceIDSchema(MaBaseSchema):
    service_id = ma.fields.String(required=True, allow_none=False)
