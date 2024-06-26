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


"""Module containing all Dtos and their Schemas for tasks in the Jobmanager API."""
from dataclasses import dataclass
from typing import Optional, Any

from flask import url_for
import marshmallow as ma

from ..flask_api_utils import MaBaseSchema

__all__ = [
    "ResultDto",
    "ResultDtoSchema",
]

from ...static.enums.result_type import ResultType


@dataclass
class ResultDto:
    id: int
    data: Any
    metadata: dict
    result_type: ResultType
    job_id: int
    deployment_id: int
    program_id: Optional[int]


class ResultDtoSchema(MaBaseSchema):
    id = ma.fields.Int(required=True, dump_only=True)
    data = ma.fields.Raw(required=True, dump_only=True)
    metadata = ma.fields.Dict(required=True, dump_only=True)
    result_type = ma.fields.Enum(enum=ResultType, required=True, dump_only=True)
    self = ma.fields.Function(lambda obj: url_for("job-api.JobResultDetailView", result_id=obj.id, job_id=obj.job_id))
    job = ma.fields.Function(lambda obj: url_for("job-api.JobDetailView", job_id=obj.job_id))
    program = ma.fields.Function(
        lambda obj: (
            url_for(
                "deployment-api.DeploymentProgramDetailsView",
                program_id=obj.program_id,
                deployment_id=obj.deployment_id,
            )
            if obj.program_id is not None
            else None
        )
    )
