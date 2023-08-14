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
from functools import cached_property

import qiskit
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


class QiskitPilot(Pilot):
    """The Qiskit Pilot"""

    LANGUAGE = AssemblerLanguage.QISKIT

    def __init__(self, job_core_dto: JobCoreDto):
        super().__init__(job_core_dto)
        self.__token = job_core_dto.token

    def execute(self, job_core_dto: JobCoreDto):
        if job_core_dto.type == JobType.IBM_RUN:
            self.__run_ibm_program(job_core_dto)
        elif job_core_dto.type == JobType.IBM_UPLOAD:
            self.__upload_program(job_core_dto)
        else:
            super().execute(job_core_dto)

    def run(self, circuit: QuantumCircuit, shots: int) -> list[ResultDataclass]:
        if self.device_name == "aer_simulator":
            return self.__run_on_aer_simulator(circuit, shots)
        else:
            return self._run_on_ibmq(circuit, shots)

    def __run_on_aer_simulator(self, circuit: QuantumCircuit, shots: int) -> list[ResultDataclass]:
        """Execute a job on the air_simulator using the qasm_simulator backend"""
        backend = qiskit.Aer.get_backend("qasm_simulator")
        result = qiskit.execute([circuit], backend=backend, shots=shots).result()
        results: list[ResultDataclass] = result_mapper.runner_result_to_db_results(result, str(circuit))
        # AerCircuit is not serializable and needs to be removed
        for res in results:
            res.meta_data.pop("circuit")

        return results
        # logging.info(f"Run job with id {job_dto.id} locally on aer_simulator and get the result {results}")

    def _run_on_ibmq(self, circuit: QuantumCircuit, shots: int) -> list[ResultDataclass]:
        """Run a job on an IBM backend using the Qiskit Pilot"""
        backend = self.ibm_provider_backend
        transpiled = transpile([circuit], backend=backend)
        logging.info("Transpiled quantum circuit(s) for a specific IBM backend")
        job_from_ibm = backend.run(transpiled, shots=shots)
        ibm_result = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.runner_result_to_db_results(ibm_result, str(circuit))
        return results

        # logging.info(
        #    f"Run job with id {job_dto.id} on {job_dto.executed_on.provider.name}  and get the result {results}"
        # )

    def sample(self, circuit: QuantumCircuit) -> list[ResultDataclass]:
        """Uses the Sampler to execute a job on an IBM backend using the Qiskit Pilot"""
        sampler = Sampler(backend=self.__runtime_service_backend)

        job_from_ibm: RuntimeJob = sampler.run([circuit])
        ibm_result: SamplerResult = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.sampler_result_to_db_results(ibm_result, [circuit])
        return results

        # logging.info(
        #    f"Run job with id {job_dto.id} on {job_dto.executed_on.provider.name}  and get the result {results}"
        # )

    def estimate(self, circuit: QuantumCircuit) -> list[ResultDataclass]:
        """Uses the Estimator to execute a job on an IBM backend using the Qiskit Pilot"""
        estimator = Estimator(backend=self.__runtime_service_backend)
        estimator_observables: list[SparsePauliOp] = [SparsePauliOp("IY"), SparsePauliOp("IY")]

        job_from_ibm = estimator.run([circuit, circuit], observables=estimator_observables)
        ibm_result: EstimatorResult = job_from_ibm.result()
        results: list[ResultDataclass] = result_mapper.estimator_result_to_db_results(ibm_result, [circuit, circuit],
                                                                                      "IY")
        return results

        # logging.info(
        #    f"Run job with id {job_dto.id} on {job_dto.executed_on.provider.name} and get the result {results}"
        # )

    @staticmethod
    def __get_file_path_to_resources(file_name):
        working_directory_path = os.path.abspath(os.getcwd())
        return os.path.join(working_directory_path, "resources", "upload_files", file_name)

    def __upload_program(self, job_core_dto: JobCoreDto):
        """Upload and then run a quantum program on the QiskitRuntimeService"""
        ibm_program_ids = []
        for program in job_core_dto.deployment.programs:
            python_file_path = self.__get_file_path_to_resources(program.python_file_path)
            python_file_metadata_path = self.__get_file_path_to_resources(program.python_file_metadata)
            ibm_program_ids.append(self.__runtime_service.upload_program(python_file_path, python_file_metadata_path))
        job_db_service.update_attribute(job_core_dto.id, JobType.IBM_RUN, JobDataclass.type)
        job_db_service.update_attribute(job_core_dto.id, JobState.READY, JobDataclass.state)
        ibm_results = [
            ResultDataclass(result_dict={"ibm_job_id": ibm_program_ids[0]}, result_type=ResultType.UPLOAD_SUCCESSFUL)
        ]
        job_db_service.update_finished_job(job_core_dto.id, ibm_results, job_state=JobState.READY)

    def __run_ibm_program(self, job_core_dto: JobCoreDto):
        ibm_results = []
        options_dict: dict = job_core_dto.ibm_file_options
        input_dict: dict = job_core_dto.ibm_file_inputs

        try:
            ibm_job_id = job_core_dto.results[0].result_dict["ibm_job_id"]
            result = self.__runtime_service.run(ibm_job_id, inputs=input_dict, options=options_dict).result()
            ibm_results.extend(result_mapper.runner_result_to_db_results(result, job_core_dto))
        except IBMRuntimeError as exception:
            logging.info("Error when accessing IBM, 403 Client Error")
            ibm_results.append(
                ResultDataclass(result_dict={"value": "403 Error when accessing"}, result_type=ResultType.ERROR)
            )
            job_db_service.update_finished_job(job_core_dto.id, ibm_results, job_state=JobState.ERROR)
            raise exception
        job_db_service.update_finished_job(job_core_dto.id, ibm_results)

    def __get_token(self):
        """Save account credentials and get provider"""
        token = self.__token
        # If the token is empty the token is taken from the environment variables.
        if (not token or token == "") and os.getenv("IBM_TOKEN") is not None:
            token = os.getenv("IBM_TOKEN")
        return token

    @cached_property
    def ibm_provider_backend(self) -> BackendV1:
        """Save account credentials and get provider"""
        # Try to save the account.

        IBMProvider.save_account(token=self.__get_token(), overwrite=True)
        return IBMProvider().get_backend(self.device_name)

    @cached_property
    def __runtime_service(self) -> QiskitRuntimeService:
        service = QiskitRuntimeService(token=None, channel=None, filename=None, name=None)
        service.save_account(token=self.__get_token(), channel="ibm_quantum", overwrite=True)
        return service

    @cached_property
    def __runtime_service_backend(self) -> BackendV1:
        return self.__runtime_service.get_backend(self.device_name)
