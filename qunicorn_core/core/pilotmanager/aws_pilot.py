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

from qunicorn_core.api.api_models.job_dtos import JobCoreDto
from qunicorn_core.core.mapper import result_mapper
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from braket.devices import LocalSimulator
from braket.ir.openqasm import Program as OpenQASMProgram
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.job_state import JobState
from braket.tasks.local_quantum_task import LocalQuantumTask

from qunicorn_core.static.enums.job_type import JobType


class AWSPilot(Pilot):
    """The AWS Pilot"""

    def execute(self, job_core_dto: JobCoreDto):
        print(f"Executing job {job_core_dto} with AWS Pilot")
        if job_core_dto.type == JobType.AWS_SIMULATOR:
            self.__localSimulation(job_core_dto)
        else:
            print("WARNING: No valid Job Type specified")

    def transpile(self, job_core_dto: JobCoreDto):
        """Transpile job for an AWS backend, needs a device_id"""
        print("Transpile a quantum circuit for a specific AWS backend")
        circuit = OpenQASMProgram(source=job_core_dto.deployment.programs[0].quantum_circuit)
        return circuit

    def __localSimulation(self, job_core_dto: JobCoreDto):
        job_db_service.update_attribute(job_core_dto.id, JobState.RUNNING, JobDataclass.state)
        # instantiate local simulator
        device = LocalSimulator()
        # define the circuit
        circuit = self.transpile(job_core_dto)
        # run the circuit
        quantumTask: LocalQuantumTask = device.run(circuit, shots=job_core_dto.shots)
        aws_simulator_result = quantumTask.result()
        # save result
        results: list[ResultDataclass] = result_mapper.aws_local_simulator_result_to_db_results(aws_simulator_result, job_core_dto)
        job_db_service.update_finished_job(job_core_dto.id, results)
