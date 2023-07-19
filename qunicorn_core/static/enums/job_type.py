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


class JobType(StrEnum):
    """Enum to save the different states of the jobs

    Values:
        RUNNER: Normal execution of a job
        SAMPLER: Samples multiple quantum programs
        ESTIMATOR: Estimates multiple quantum programs
    """

    RUNNER = "RUNNER"
    SAMPLER = "SAMPLER"
    ESTIMATOR = "ESTIMATOR"
    IBM_RUN = "IBM_RUN"
    IBM_UPLOAD = "IBM_UPLOAD"
