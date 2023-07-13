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
import json
import os
from typing import List

from qiskit import QuantumCircuit, transpile
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit.providers import BackendV1
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_provider import IBMProvider
from qiskit_ibm_provider.api.exceptions import RequestsApiError
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Estimator, RuntimeJob

from qunicorn_core.api.api_models import JobCoreDto
from qunicorn_core.core.mapper import result_mapper
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.result_type import ResultType


class QiskitPilot(Pilot):
    """The Qiskit Pilot"""

    IBMQ_BACKEND = "ibmq_qasm_simulator"

    def execute(self, job_core_dto: JobCoreDto):
        """Execute the job regarding his JobType"""
        if job_core_dto.type == JobType.RUNNER:
            self.__run(job_core_dto)
        elif job_core_dto.type == JobType.ESTIMATOR:
            self.__estimate(job_core_dto)
        elif job_core_dto.type == JobType.SAMPLER:
            self.__sample(job_core_dto)
        elif job_core_dto.type == JobType.FILE:
            self.__upload_and_run_program(job_core_dto)
        else:
            print("WARNING: No valid Job Type specified")

    def __run(self, job_dto: JobCoreDto):
        """Run a job on an IBM backend using the Qiskit Pilot"""
        provider = self.__get_ibm_provider_and_login(job_dto.token, job_dto.id)
        backend, transpiled = self.transpile(provider, job_dto)
        job_db_service.update_attribute(job_dto.id, JobState.RUNNING, JobDataclass.state)

        job_from_ibm = backend.run(transpiled, shots=job_dto.shots)
        ibm_result = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.runner_result_to_db_results(ibm_result, job_dto)
        job_db_service.update_finished_job(job_dto.id, results)
        print(f"Run job {job_from_ibm} with id {job_dto.id} on {job_dto.executed_on.provider.name}  and get the result {results}")

    def __sample(self, job_dto: JobCoreDto):
        """Uses the Sampler to execute a job on an IBM backend using the Qiskit Pilot"""
        backend, circuits = self.__get_backend_circuits_and_id_for_qiskit_runtime(job_dto)
        sampler = Sampler(session=backend)

        job_from_ibm: RuntimeJob = sampler.run(circuits)
        ibm_result: SamplerResult = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.sampler_result_to_db_results(ibm_result, job_dto)
        job_db_service.update_finished_job(job_dto.id, results)
        print(f"Run job {job_from_ibm} with id {job_dto.id} on {job_dto.executed_on.provider.name}  and get the result {results}")

    def __estimate(self, job_dto: JobCoreDto):
        """Uses the Estimator to execute a job on an IBM backend using the Qiskit Pilot"""
        backend, circuits = self.__get_backend_circuits_and_id_for_qiskit_runtime(job_dto)
        estimator = Estimator(session=backend)
        estimator_observables: list[SparsePauliOp] = [SparsePauliOp("IY"), SparsePauliOp("IY")]

        job_from_ibm = estimator.run(circuits, observables=estimator_observables)
        ibm_result: EstimatorResult = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.estimator_result_to_db_results(ibm_result, job_dto, "IY")
        job_db_service.update_finished_job(job_dto.id, results)
        print(f"Run job {job_from_ibm} with id {job_dto.id} on {job_dto.executed_on.provider.name}  and get the result {results}")

    def __get_backend_circuits_and_id_for_qiskit_runtime(self, job_dto):
        """Instantiate all important configurations and updates the job_state"""
        service: QiskitRuntimeService = QiskitRuntimeService()
        self.__get_ibm_provider_and_login(job_dto.token, job_dto.id)
        job_db_service.update_attribute(job_dto.id, JobState.RUNNING, JobDataclass.state)
        circuits: List[QuantumCircuit] = QiskitPilot.__get_circuits_as_QuantumCircuits(job_dto)
        backend: BackendV1 = service.get_backend(self.IBMQ_BACKEND)
        return backend, circuits

    @staticmethod
    def __get_circuits_as_QuantumCircuits(job_dto: JobCoreDto) -> List[QuantumCircuit]:
        """Transforms the circuit string into IBM QuantumCircuit objects"""
        return [QuantumCircuit().from_qasm_str(program.quantum_circuit) for program in job_dto.deployment.programs]

    @staticmethod
    def __get_ibm_provider_and_login(token: str, job_dto_id: int) -> IBMProvider:
        """Save account credentials and get provider"""

        # If the token is empty the token is taken from the environment variables.
        if token == "" and os.getenv("IBM_TOKEN") is not None:
            token = os.getenv("IBM_TOKEN")

        # Try to save the account. Update job_dto to job_state = Error, if it is not possible
        try:
            IBMProvider.save_account(token=token, overwrite=True)
        except RequestsApiError:
            job_db_service.update_attribute(job_dto_id, JobState.ERROR, JobDataclass.state)
            raise ValueError("The passed token is not valid.")

        # Load previously saved account credentials.
        return IBMProvider()

    def transpile(self, provider: IBMProvider, job_dto: JobCoreDto):
        """Transpile job on an IBM backend"""

        circuits: list[QuantumCircuit] = self.__get_circuits_as_QuantumCircuits(job_dto)
        backend = provider.get_backend(self.IBMQ_BACKEND)
        transpiled = transpile(circuits, backend=backend)
        print("Transpiled quantum circuit(s) for a specific IBM backend")
        return backend, transpiled

    @staticmethod
    def __get_file_path_to_resources(file_name):
        working_directory_path = os.path.abspath(os.getcwd())
        return working_directory_path + os.sep + "resources" + os.sep + "upload_files" + os.sep + file_name

    def __upload_and_run_program(self, job_core_dto):
        """Upload and then run a quantum program on the QiskitRuntimeService"""

        service = QiskitRuntimeService()
        service.save_account(token=job_core_dto.token, channel="ibm_quantum", overwrite=True)
        ibm_program_ids = []
        for program in job_core_dto.deployment.programs:
            python_file_path = self.__get_file_path_to_resources(program.python_file_path)
            python_file_metadata_path = self.__get_file_path_to_resources(program.python_file_metadata)
            ibm_program_ids.append(service.upload_program(python_file_path, python_file_metadata_path))
        for ibm_program_id in ibm_program_ids:
            options_dict = json.loads(program.python_file_options)
            input_dict = json.loads(program.python_file_inputs)
            service.run(ibm_program_id, inputs=input_dict, options=options_dict)
        job_db_service.update_finished_job(job_core_dto.id, [])
