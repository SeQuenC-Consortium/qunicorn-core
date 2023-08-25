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
import os
from typing import List

import qiskit
from braket.circuits import Circuit
from braket.circuits.serialization import IRType
from qiskit import QuantumCircuit, transpile
from qiskit.primitives import SamplerResult, EstimatorResult
from qiskit.providers import BackendV1
from qiskit.qasm import QasmError
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_provider import IBMProvider
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Estimator, RuntimeJob, IBMRuntimeError

from qunicorn_core.api.api_models import JobCoreDto
from qunicorn_core.core.mapper import result_mapper
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.util import logging


class IBMPilot(Pilot):
    """The IBM Pilot"""

    def execute(self, job_core_dto: JobCoreDto):
        """Execute a job on an IBM backend using the IBM Pilot"""

        if job_core_dto.type == JobType.RUNNER:
            if job_core_dto.executed_on.device_name == "aer_simulator":
                self.__execute_on_aer_simulator(job_core_dto)
            else:
                self.__run(job_core_dto)
        elif job_core_dto.type == JobType.ESTIMATOR:
            self.__estimate(job_core_dto)
        elif job_core_dto.type == JobType.SAMPLER:
            self.__sample(job_core_dto)
        elif job_core_dto.type == JobType.IBM_RUN:
            self.__run_ibm_program(job_core_dto)
        elif job_core_dto.type == JobType.IBM_UPLOAD:
            self.__upload_program(job_core_dto)
        else:
            exception: Exception = ValueError("No valid Job Type specified")
            results = result_mapper.exception_to_error_results(exception)
            job_db_service.update_finished_job(job_core_dto.id, results, JobState.ERROR)
            raise exception

    def __execute_on_aer_simulator(self, job_dto: JobCoreDto):
        """Execute a job on the air_simulator using the qasm_simulator backend"""
        job_id = job_dto.id

        job_db_service.update_attribute(job_id, JobState.RUNNING, JobDataclass.state)
        circuits = self.__get_circuits_as_QuantumCircuits(job_dto)
        backend = qiskit.Aer.get_backend("qasm_simulator")
        result = qiskit.execute(circuits, backend=backend, shots=job_dto.shots).result()

        results: list[ResultDataclass] = result_mapper.ibm_runner_to_dataclass(result, job_dto)
        # AerCircuit is not serializable and needs to be removed
        for res in results:
            if res is not None and "circuit" in res.meta_data:
                res.meta_data.pop("circuit")
        job_db_service.update_finished_job(job_id, results)
        logging.info(f"Run job with id {job_dto.id} locally on aer_simulator and get the result {results}")

    def __run(self, job_dto: JobCoreDto):
        """Run a job on an IBM backend using the IBM Pilot"""
        provider = self.__get_ibm_provider_login_and_update_job(job_dto.token, job_dto.id)
        backend, transpiled = self.transpile(provider, job_dto)
        job_db_service.update_attribute(job_dto.id, JobState.RUNNING, JobDataclass.state)

        job_from_ibm = backend.run(transpiled, shots=job_dto.shots)
        ibm_result = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.ibm_runner_to_dataclass(ibm_result, job_dto)
        job_db_service.update_finished_job(job_dto.id, results)
        logging.info(
            f"Run job with id {job_dto.id} on {job_dto.executed_on.provider.name}  and get the result {results}"
        )

    def __sample(self, job_dto: JobCoreDto):
        """Uses the Sampler to execute a job on an IBM backend using the IBM Pilot"""
        backend, circuits = self.__get_backend_circuits_and_id_for_qiskit_runtime(job_dto)
        sampler = Sampler(session=backend)

        job_from_ibm: RuntimeJob = sampler.run(circuits)
        ibm_result: SamplerResult = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.ibm_sampler_to_dataclass(ibm_result, job_dto)
        job_db_service.update_finished_job(job_dto.id, results)
        logging.info(
            f"Run job with id {job_dto.id} on {job_dto.executed_on.provider.name}  and get the result {results}"
        )

    def __estimate(self, job_dto: JobCoreDto):
        """Uses the Estimator to execute a job on an IBM backend using the IBM Pilot"""
        backend, circuits = self.__get_backend_circuits_and_id_for_qiskit_runtime(job_dto)
        estimator = Estimator(session=backend)
        estimator_observables: list[SparsePauliOp] = [SparsePauliOp("IY"), SparsePauliOp("IY")]

        job_from_ibm = estimator.run(circuits, observables=estimator_observables)
        ibm_result: EstimatorResult = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.ibm_estimator_to_dataclass(ibm_result, job_dto, "IY")
        job_db_service.update_finished_job(job_dto.id, results)
        logging.info(
            f"Run job with id {job_dto.id} on {job_dto.executed_on.provider.name} and get the result {results}"
        )

    def __get_backend_circuits_and_id_for_qiskit_runtime(self, job_dto):
        """Instantiate all important configurations and updates the job_state"""
        self.__get_ibm_provider_login_and_update_job(job_dto.token, job_dto.id)
        service: QiskitRuntimeService = QiskitRuntimeService()
        job_db_service.update_attribute(job_dto.id, JobState.RUNNING, JobDataclass.state)
        circuits: List[QuantumCircuit] = IBMPilot.__get_circuits_as_QuantumCircuits(job_dto)
        backend: BackendV1 = service.get_backend(job_dto.executed_on.device_name)
        return backend, circuits

    qc = None

    @staticmethod
    def __get_circuits_as_QuantumCircuits(job_dto: JobCoreDto) -> list[QuantumCircuit]:
        """Transforms the circuit string into IBM QuantumCircuit objects"""
        circuits: list[QuantumCircuit] = []
        error_results: list[ResultDataclass] = []

        # transform each circuit into a QuantumCircuit-Object
        for program in job_dto.deployment.programs:
            try:
                if program.assembler_language == AssemblerLanguage.QASM:
                    circuits.append(QuantumCircuit().from_qasm_str(program.quantum_circuit))
                elif program.assembler_language == AssemblerLanguage.QISKIT:
                    _locals = locals()
                    exec(program.quantum_circuit, globals(), _locals)
                    circuit: QuantumCircuit = qc
                    circuits.append(circuit)
            except QasmError as exception:
                error_results.extend(result_mapper.exception_to_error_results(exception, program.quantum_circuit))

        # If an error was caught -> Update the job and raise it again
        if len(error_results) > 0:
            job_db_service.update_finished_job(job_dto.id, error_results, JobState.ERROR)
            raise QasmError("Invalide Qasm String.")

        return circuits

    @staticmethod
    def get_ibm_provider_and_login(token: str) -> IBMProvider:
        """Save account credentials and get provider"""

        # If the token is empty the token is taken from the environment variables.
        if token == "" and os.getenv("IBM_TOKEN") is not None:
            token = os.getenv("IBM_TOKEN")

        # Try to save the account. Update job_dto to job_state = Error, if it is not possible
        IBMProvider.save_account(token=token, overwrite=True)
        return IBMProvider()

    @staticmethod
    def __get_ibm_provider_login_and_update_job(token: str, job_dto_id: int) -> IBMProvider:
        """Save account credentials, get provider and update job_dto to job_state = Error, if it is not possible"""
        try:
            return IBMPilot.get_ibm_provider_and_login(token)
        except Exception as exception:
            job_db_service.update_finished_job(
                job_dto_id, result_mapper.exception_to_error_results(exception), JobState.ERROR
            )
            raise exception

    def transpile(self, provider: IBMProvider, job_dto: JobCoreDto):
        """Transpile job on an IBM backend"""

        # TODO this can be used for the universal QASM translation for AWS and IBM - currently the resulting QSAM String
        #  can be invalid
        for program in job_dto.deployment.programs:
            if program.assembler_language == AssemblerLanguage.BRAKET:
                circuit: Circuit = eval(program.quantum_circuit)
                program.quantum_circuit = circuit.to_ir(IRType.OPENQASM).source
                print("Converted String vom BRAKET to QASM for IBM:", program.quantum_circuit)
        # ############################################################################################

        circuits: list[QuantumCircuit] = self.__get_circuits_as_QuantumCircuits(job_dto)

        backend = provider.get_backend(job_dto.executed_on.device_name)
        transpiled = transpile(circuits, backend=backend)

        logging.info("Transpiled quantum circuit(s) for a specific IBM backend")
        return backend, transpiled

    @staticmethod
    def __get_file_path_to_resources(file_name):
        working_directory_path = os.path.abspath(os.getcwd())
        return working_directory_path + os.sep + "resources" + os.sep + "upload_files" + os.sep + file_name

    def __upload_program(self, job_core_dto: JobCoreDto):
        """Upload and then run a quantum program on the QiskitRuntimeService"""
        service = self.__get_runtime_service(job_core_dto)
        ibm_program_ids = []
        for program in job_core_dto.deployment.programs:
            python_file_path = self.__get_file_path_to_resources(program.python_file_path)
            python_file_metadata_path = self.__get_file_path_to_resources(program.python_file_metadata)
            ibm_program_ids.append(service.upload_program(python_file_path, python_file_metadata_path))
        job_db_service.update_attribute(job_core_dto.id, JobType.IBM_RUN, JobDataclass.type)
        job_db_service.update_attribute(job_core_dto.id, JobState.READY, JobDataclass.state)
        ibm_results = [
            ResultDataclass(result_dict={"ibm_job_id": ibm_program_ids[0]}, result_type=ResultType.UPLOAD_SUCCESSFUL)
        ]
        job_db_service.update_finished_job(job_core_dto.id, ibm_results, job_state=JobState.READY)

    def __run_ibm_program(self, job_core_dto: JobCoreDto):
        service = self.__get_runtime_service(job_core_dto)
        ibm_results = []
        options_dict: dict = job_core_dto.ibm_file_options
        input_dict: dict = job_core_dto.ibm_file_inputs

        try:
            ibm_job_id = job_core_dto.results[0].result_dict["ibm_job_id"]
            result = service.run(ibm_job_id, inputs=input_dict, options=options_dict).result()
            ibm_results.extend(result_mapper.ibm_runner_to_dataclass(result, job_core_dto))
        except IBMRuntimeError as exception:
            logging.info("Error when accessing IBM, 403 Client Error")
            ibm_results.append(
                ResultDataclass(result_dict={"value": "403 Error when accessing"}, result_type=ResultType.ERROR)
            )
            job_db_service.update_finished_job(job_core_dto.id, ibm_results, job_state=JobState.ERROR)
            raise exception
        job_db_service.update_finished_job(job_core_dto.id, ibm_results)

    @staticmethod
    def __get_runtime_service(job_core_dto) -> QiskitRuntimeService:
        if job_core_dto.token == "" and os.getenv("IBM_TOKEN") is not None:
            job_core_dto.token = os.getenv("IBM_TOKEN")

        service = QiskitRuntimeService(token=None, channel=None, filename=None, name=None)
        service.save_account(token=job_core_dto.token, channel="ibm_quantum", overwrite=True)
        return service
