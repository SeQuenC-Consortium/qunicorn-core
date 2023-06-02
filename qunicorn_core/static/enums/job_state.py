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

from enum import Enum


class JobState(Enum):
    """Enum to save the different states of the jobs

    Values:
        READY: Job is ready to use
        RUNNING: Job is currently executing a quantum circuit
        FINISHED: Job finished the executing
        BLOCKED: Job is blocked, and cannot be used for other purposes
        ERROR: When an error occurred while executing a quantum circuit
    """

    READY = 1
    RUNNING = 2
    FINISHED = 3
    BLOCKED = 4
    ERROR = 5
