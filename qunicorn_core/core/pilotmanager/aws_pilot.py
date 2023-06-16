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


from qunicorn_core.core.pilotmanager.base_pilot import Pilot


class AWSPilot(Pilot):
    """The AWS Pilot"""

    def execute(self, job):
        print(f"Executing job {job} with AWS Pilot")

    def transpile(self, job):
        """Transpile job on an IBM backend, needs a device_id"""

        print(f"Transpile a quantum circuit for a specific AWS backend")
