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
from braket.circuits import Circuit
from braket.devices import LocalSimulator
from braket.ir.openqasm import Program as OpenQASMProgram
from braket.tasks import GateModelQuantumTaskResult
from braket.tasks.local_quantum_task_batch import LocalQuantumTaskBatch

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

    def execute(self, job_core_dto: JobCoreDto):
        """Execute a job with AWS Pilot and saves results in the database"""

        logging.info(f"Executing job {job_core_dto} with AWS Pilot")
        if job_core_dto.type == JobType.RUNNER:
            if job_core_dto.executed_on.device_name == "local_simulator":
                self.__local_simulation(job_core_dto)
            else:
                exception: Exception = ValueError("No valid device specified")
                raise exception
        else:
            exception: Exception = ValueError("No valid Job Type specified")
            results = result_mapper.get_error_results(exception)
            job_db_service.update_finished_job(job_core_dto.id, results, JobState.ERROR)
            raise exception

    @staticmethod
    def transpile(job_core_dto: JobCoreDto):
        """Transpile job for an AWS backend"""
        logging.info("Transpile a quantum circuit for a specific AWS backend")
        transpiled_programs = []

        # TODO add exception handing - if language does not match syntax
        for program in job_core_dto.deployment.programs:
            if program.assembler_language == AssemblerLanguage.QASM:
                transpiled_programs.append(OpenQASMProgram(source=program.quantum_circuit))
            elif program.assembler_language == AssemblerLanguage.BRAKET:
                circuit: Circuit = eval(program.quantum_circuit)
                transpiled_programs.append(circuit)

        return transpiled_programs

    def __local_simulation(self, job_core_dto: JobCoreDto):
        """Execute the job on a local simulator and saves results in the database"""

        job_db_service.update_attribute(job_core_dto.id, JobState.RUNNING, JobDataclass.state)
        device = LocalSimulator()
        circuits = self.transpile(job_core_dto)

        quantum_tasks: LocalQuantumTaskBatch = device.run_batch(circuits, shots=job_core_dto.shots)
        aws_simulator_results: list[GateModelQuantumTaskResult] = quantum_tasks.results()
        results: list[ResultDataclass] = result_mapper.aws_local_simulator_result_to_db_results(
            aws_simulator_results, job_core_dto
        )

        job_db_service.update_finished_job(job_core_dto.id, results)
