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

from braket.devices import LocalSimulator
from braket.ir.openqasm import Program as OpenQASMProgram
from braket.tasks.local_quantum_task import LocalQuantumTask

from qunicorn_core.api.api_models.job_dtos import JobCoreDto
from qunicorn_core.core.mapper import result_mapper
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.util import logging


class AWSPilot(Pilot):
    """The AWS Pilot"""

    LANGUAGE = AssemblerLanguage.BRAKET

    def run(self, circuit, shots: int) -> list[ResultDataclass]:
        """Run a job with AWS Pilot and saves results in the database"""

        if self.device_name == "local_simulator":
            return self.__local_simulation(circuit, shots)
        else:
            exception: Exception = ValueError("No valid device specified")
            raise exception

    def __local_simulation(self, circuit, shots: int):
        """Execute the job on a local simulator and saves results in the database"""

        device = LocalSimulator()
        quantum_task: LocalQuantumTask = device.run(circuit, shots=shots)
        aws_simulator_result = quantum_task.result()
        results: list[ResultDataclass] = result_mapper.aws_local_simulator_result_to_db_results(
            aws_simulator_result, str(circuit)
        )
        return results
