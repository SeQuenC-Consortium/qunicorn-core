# Copyright 2023 University of Stuttgart.
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

from enum import StrEnum

from qunicorn_core.static.enums.job_type import JobType


class ResultType(StrEnum):
    """Enum to save the different result types

    Values:
        COUNTS: Classical result of a RUNNER
        QUASI_DIST: Classical result of an ESTIMATOR
        VALUE_AND_VARIANCE: Classical result of a SAMPLER
        ERROR: Classical result of an ERROR
        UPLOAD_SUCCESSFUL: Classical result of an UPLOAD
    """

    COUNTS = "COUNTS"
    QUASI_DIST = "QUASI_DIST"
    VALUE_AND_VARIANCE = "VALUE_AND_VARIANCE"
    ERROR = "ERROR"
    UPLOAD_SUCCESSFUL = "UPLOAD_SUCCESSFUL"

    @staticmethod
    def get_result_type(job_type: JobType):
        if job_type == JobType.RUNNER:
            return ResultType.COUNTS
        elif job_type == JobType.SAMPLER:
            return ResultType.QUASI_DIST
        else:
            return ResultType.VALUE_AND_VARIANCE
