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
from datetime import datetime

import qiskit
from qiskit.primitives import EstimatorResult, SamplerResult
from qiskit.providers import BackendV1
from qiskit.quantum_info import SparsePauliOp
from qiskit.result import Result
from qiskit_ibm_provider import IBMProvider
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Estimator, RuntimeJob, IBMRuntimeError

from qunicorn_core.api.api_models import JobCoreDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import job_db_service, device_db_service, provider_db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.db.models.user import UserDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.util import logging, utils


class IBMPilot(Pilot):
    """The IBM Pilot"""

    provider_name: ProviderName = ProviderName.IBM

    supported_language: AssemblerLanguage = AssemblerLanguage.QISKIT

    def execute_provider_specific(self, job_core_dto: JobCoreDto):
        """Execute a job of a provider specific type on a backend using a Pilot"""

        if job_core_dto.type == JobType.ESTIMATOR:
            return self.__estimate(job_core_dto)
        elif job_core_dto.type == JobType.SAMPLER:
            return self.__sample(job_core_dto)
        elif job_core_dto.type == JobType.FILE_RUNNER:
            return self.__run_program(job_core_dto)
        elif job_core_dto.type == JobType.FILE_UPLOAD:
            return self.__upload_program(job_core_dto)
        else:
            raise job_db_service.return_exception_and_update_job(
                job_core_dto.id, ValueError("No valid Job Type specified")
            )

    def run(self, job_dto: JobCoreDto):
        """Execute a job local using aer simulator or a real backend"""

        if job_dto.executed_on.is_local:
            backend = qiskit.Aer.get_backend("qasm_simulator")
        else:
            provider = self.__get_provider_login_and_update_job(job_dto.token, job_dto.id)
            backend = provider.get_backend(job_dto.executed_on.name)

        result = qiskit.execute(job_dto.transpiled_circuits, backend=backend, shots=job_dto.shots).result()
        results: list[ResultDataclass] = IBMPilot.__map_runner_results_to_dataclass(result, job_dto)

        # AerCircuit is not serializable and needs to be removed
        for res in results:
            if res is not None and "circuit" in res.meta_data:
                res.meta_data.pop("circuit")

        return results

    def __sample(self, job_dto: JobCoreDto):
        """Uses the Sampler to execute a job on an IBM backend using the IBM Pilot"""

        backend, circuits = self.__get_backend_and_circuits_for_qiskit_runtime(job_dto)
        sampler = Sampler(session=backend)
        job_from_ibm: RuntimeJob = sampler.run(circuits)
        ibm_result: SamplerResult = job_from_ibm.result()
        return IBMPilot._map_sampler_results_to_dataclass(ibm_result, job_dto)

    def __estimate(self, job_dto: JobCoreDto):
        """Uses the Estimator to execute a job on an IBM backend using the IBM Pilot"""

        backend, circuits = self.__get_backend_and_circuits_for_qiskit_runtime(job_dto)
        estimator = Estimator(session=backend)
        job_from_ibm = estimator.run(circuits, observables=[SparsePauliOp("IY"), SparsePauliOp("IY")])
        ibm_result: EstimatorResult = job_from_ibm.result()
        return IBMPilot._map_estimator_results_to_dataclass(ibm_result, job_dto, "IY")

    def __get_backend_and_circuits_for_qiskit_runtime(self, job_dto):
        """Instantiate all important configurations and updates the job_state"""

        self.__get_provider_login_and_update_job(job_dto.token, job_dto.id)
        service: QiskitRuntimeService = QiskitRuntimeService()
        backend: BackendV1 = service.get_backend(job_dto.executed_on.name)
        return backend, job_dto.transpiled_circuits

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
    def __get_provider_login_and_update_job(token: str, job_dto_id: int) -> IBMProvider:
        """Save account credentials, get provider and update job_dto to job_state = Error, if it is not possible"""

        try:
            return IBMPilot.get_ibm_provider_and_login(token)
        except Exception as exception:
            raise job_db_service.return_exception_and_update_job(job_dto_id, exception)

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
        job_db_service.update_attribute(job_core_dto.id, JobType.FILE_RUNNER, JobDataclass.type)
        job_db_service.update_attribute(job_core_dto.id, JobState.READY, JobDataclass.state)
        ibm_results = [
            ResultDataclass(result_dict={"ibm_job_id": ibm_program_ids[0]}, result_type=ResultType.UPLOAD_SUCCESSFUL)
        ]
        job_db_service.update_finished_job(job_core_dto.id, ibm_results, job_state=JobState.READY)

    def __run_program(self, job_core_dto: JobCoreDto):
        service = self.__get_runtime_service(job_core_dto)
        ibm_results = []
        options_dict: dict = job_core_dto.ibm_file_options
        input_dict: dict = job_core_dto.ibm_file_inputs

        try:
            ibm_job_id = job_core_dto.results[0].result_dict["ibm_job_id"]
            result = service.run(ibm_job_id, inputs=input_dict, options=options_dict).result()
            ibm_results.extend(IBMPilot.__map_runner_results_to_dataclass(result, job_core_dto))
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

    @staticmethod
    def __map_runner_results_to_dataclass(ibm_result: Result, job_dto: JobCoreDto) -> list[ResultDataclass]:
        result_dtos: list[ResultDataclass] = []

        for i in range(len(ibm_result.results)):
            counts: dict = ibm_result.results[i].data.counts
            circuit: str = job_dto.deployment.programs[i].quantum_circuit
            result_dtos.append(
                ResultDataclass(
                    circuit=circuit,
                    result_dict=counts,
                    result_type=ResultType.COUNTS,
                    meta_data=ibm_result.results[i].to_dict(),
                )
            )
        return result_dtos

    @staticmethod
    def _map_estimator_results_to_dataclass(
        ibm_result: EstimatorResult, job: JobCoreDto, observer: str
    ) -> list[ResultDataclass]:
        result_dtos: list[ResultDataclass] = []
        for i in range(ibm_result.num_experiments):
            value: float = ibm_result.values[i]
            variance: float = ibm_result.metadata[i]["variance"]
            circuit: str = job.deployment.programs[i].quantum_circuit
            result_dtos.append(
                ResultDataclass(
                    circuit=circuit,
                    result_dict={"value": str(value), "variance": str(variance)},
                    result_type=ResultType.VALUE_AND_VARIANCE,
                    meta_data={"observer": f"SparsePauliOp-{observer}"},
                )
            )
        return result_dtos

    @staticmethod
    def _map_sampler_results_to_dataclass(ibm_result: SamplerResult, job_dto: JobCoreDto) -> list[ResultDataclass]:
        result_dtos: list[ResultDataclass] = []
        for i in range(ibm_result.num_experiments):
            quasi_dist: dict = ibm_result.quasi_dists[i]
            circuit: str = job_dto.deployment.programs[i].quantum_circuit
            result_dtos.append(
                ResultDataclass(
                    circuit=circuit,
                    result_dict=quasi_dist,
                    result_type=ResultType.QUASI_DIST,
                )
            )
        return result_dtos

    def get_standard_provider(self):
        return ProviderDataclass(with_token=True, supported_language=self.supported_language, name=self.provider_name)

    def get_standard_job_with_deployment(self, user: UserDataclass, device: DeviceDataclass) -> JobDataclass:
        language: AssemblerLanguage = AssemblerLanguage.QASM2
        programs: list[QuantumProgramDataclass] = [
            QuantumProgramDataclass(quantum_circuit=utils.get_default_qasm_string(1), assembler_language=language),
            QuantumProgramDataclass(quantum_circuit=utils.get_default_qasm_string(2), assembler_language=language),
        ]
        deployment = DeploymentDataclass(
            deployed_by=user,
            programs=programs,
            deployed_at=datetime.now(),
            name="DeploymentIBMQasmName",
        )

        return JobDataclass(
            executed_by=user,
            executed_on=device,
            deployment=deployment,
            progress=0,
            state=JobState.READY,
            shots=4000,
            type=JobType.RUNNER,
            started_at=datetime.now(),
            name="IMBJob",
            results=[ResultDataclass(result_dict={"0x": "550", "1x": "450"})],
        )

    def save_devices_from_provider(self, device_request):
        ibm_provider: IBMProvider = IBMPilot.get_ibm_provider_and_login(device_request.token)
        all_devices = ibm_provider.backends()
        provider: ProviderDataclass = provider_db_service.get_provider_by_name(self.provider_name)
        for ibm_device in all_devices:
            device: DeviceDataclass = DeviceDataclass(
                name=ibm_device.name,
                num_qubits=-1 if ibm_device.name.__contains__("stabilizer") else ibm_device.num_qubits,
                is_simulator=ibm_device.name.__contains__("simulator"),
                is_local=False,
                provider_id=provider.id,
                provider=provider,
            )
            device_db_service.save_device_by_name(device)

        device: DeviceDataclass = DeviceDataclass(
            name="aer_simulator",
            num_qubits=-1,
            is_simulator=True,
            is_local=True,
            provider_id=provider.id,
            provider=provider,
        )
        device_db_service.save_device_by_name(device)
