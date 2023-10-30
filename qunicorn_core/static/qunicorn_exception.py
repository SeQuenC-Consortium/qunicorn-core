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

"""File to store all costume exceptions used in qunicorn"""


class QunicornError(Exception):
    """General Exception raised for errors in qunicorn"""

    # Status code that will be visible in the swagger api
    status_code: int

    def __init__(self, msg, status_code=404):
        super().__init__(msg)
        self.status_code = status_code
