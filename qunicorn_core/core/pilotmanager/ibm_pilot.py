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
from typing import Optional

import qiskit
from qiskit.primitives import EstimatorResult, SamplerResult, Sampler as LocalSampler, Estimator as LocalEstimator
from qiskit.providers import QiskitBackendNotFoundError
from qiskit.quantum_info import SparsePauliOp
from qiskit.result import Result
from qiskit_ibm_provider import IBMProvider
from qiskit_ibm_runtime import (
    QiskitRuntimeService,
    Sampler,
    Estimator,
    RuntimeJob,
    IBMRuntimeError,
)

from qunicorn_core.api.api_models import JobCoreDto, DeviceDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import job_db_service, device_db_service, provider_db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.provider_assembler_language import ProviderAssemblerLanguageDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.util import logging, utils

ENABLE_EXPERIMENTAL_FEATURES = os.environ.get("ENABLE_EXPERIMENTAL_FEATURES")


class IBMPilot(Pilot):
    """The IBM Pilot"""

    provider_name: ProviderName = ProviderName.IBM

    supported_languages: list[AssemblerLanguage] = [AssemblerLanguage.QISKIT]

    def execute_provider_specific(self, job_core_dto: JobCoreDto):
        """Execute a job of a provider specific type on a backend using a Pilot"""

        if job_core_dto.type == JobType.ESTIMATOR:
            return self.__estimate(job_core_dto)
        elif job_core_dto.type == JobType.SAMPLER:
            return self.__sample(job_core_dto)
        elif job_core_dto.type == JobType.IBM_RUNNER:
            return self.__run_ibm_program(job_core_dto)
        elif job_core_dto.type == JobType.IBM_UPLOAD:
            return self.__upload_ibm_program(job_core_dto)
        else:
            raise job_db_service.return_exception_and_update_job(
                job_core_dto.id, ValueError("No valid Job Type specified")
            )

    def run(self, job_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute a job local using aer simulator or a real backend"""

        if job_dto.executed_on.is_local:
            backend = qiskit.Aer.get_backend("qasm_simulator")
        else:
            provider = self.__get_provider_login_and_update_job(job_dto.token, job_dto.id)
            backend = provider.get_backend(job_dto.executed_on.name)

        job = qiskit.execute(job_dto.transpiled_circuits, backend=backend, shots=job_dto.shots)
        job_db_service.update_attribute(job_dto.id, job.job_id(), JobDataclass.provider_specific_id)
        result = job.result()
        results: list[ResultDataclass] = IBMPilot.__map_runner_results_to_dataclass(result, job_dto)

        # AerCircuit is not serializable and needs to be removed
        for res in results:
            if res is not None and "circuit" in res.meta_data:
                res.meta_data.pop("circuit")

        return results

    def cancel_provider_specific(self, job_dto: JobCoreDto):
        """Cancel a job on an IBM backend using the IBM Pilot"""
        job = self.__get_qiskit_job_from_qiskit_runtime(job_dto)
        job.cancel()
        job_db_service.update_attribute(job_dto.id, JobState.CANCELED, JobDataclass.state)
        logging.info(f"Cancel job with id {job_dto.id} on {job_dto.executed_on.provider.name} successful.")

    def __sample(self, job_dto: JobCoreDto):
        """Uses the Sampler to execute a job on an IBM backend using the IBM Pilot"""
        if job_dto.executed_on.is_local:
            sampler = LocalSampler()
        else:
            sampler = Sampler(session=self.__get_qiskit_runtime_backend(job_dto))
        job_from_ibm: RuntimeJob = sampler.run(job_dto.transpiled_circuits)
        ibm_result: SamplerResult = job_from_ibm.result()
        return IBMPilot._map_sampler_results_to_dataclass(ibm_result, job_dto)

    def __estimate(self, job_dto: JobCoreDto) -> list[ResultDataclass]:
        """Uses the Estimator to execute a job on an IBM backend using the IBM Pilot"""
        observables: list = [SparsePauliOp("IY"), SparsePauliOp("IY")]
        if job_dto.executed_on.is_local:
            estimator = LocalEstimator()
        else:
            estimator = Estimator(session=self.__get_qiskit_runtime_backend(job_dto))
        job_from_ibm = estimator.run(job_dto.transpiled_circuits, observables=observables)
        ibm_result: EstimatorResult = job_from_ibm.result()
        return IBMPilot._map_estimator_results_to_dataclass(ibm_result, job_dto, "IY")

    def __get_qiskit_runtime_backend(self, job_dto):
        """Instantiate all important configurations and updates the job_state"""

        self.__get_provider_login_and_update_job(job_dto.token, job_dto.id)
        return QiskitRuntimeService().get_backend(job_dto.executed_on.name)

    def __get_qiskit_job_from_qiskit_runtime(self, job_dto: JobCoreDto):
        """Returns the job of the provider specific ID created on the given account"""

        self.__get_provider_login_and_update_job(job_dto.token, job_dto.id)
        service: QiskitRuntimeService = QiskitRuntimeService()
        return service.job(job_dto.provider_specific_id)

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
    def __get_file_path_to_resources(file_name) -> str:
        working_directory_path = os.path.abspath(os.getcwd())
        return working_directory_path + os.sep + "resources" + os.sep + "upload_files" + os.sep + file_name

    def __upload_ibm_program(self, job_core_dto: JobCoreDto):
        """EXPERIMENTAL"""
        """Upload and then run a quantum program on the QiskitRuntimeService"""
        if not utils.are_experimental_features_enabled():
            raise job_db_service.return_exception_and_update_job(
                job_core_dto.id,
                ValueError(
                    "Running uploaded IBM Programs is experimental and was not fully tested. Set "
                    "ENABLE_EXPERIMENTAL_FEATURES to True to enable this feature."
                ),
            )
        logging.warn("This function is experimental and could not be fully tested yet")

        service = self.__get_runtime_service(job_core_dto)
        ibm_program_ids = []
        for program in job_core_dto.deployment.programs:
            python_file_path = self.__get_file_path_to_resources(program.python_file_path)
            python_file_metadata_path = self.__get_file_path_to_resources(program.python_file_metadata)
            ibm_program_ids.append(service.upload_program(python_file_path, python_file_metadata_path))
        job_db_service.update_attribute(job_core_dto.id, JobType.IBM_RUNNER, JobDataclass.type)
        job_db_service.update_attribute(job_core_dto.id, JobState.READY, JobDataclass.state)
        ibm_results = [
            ResultDataclass(result_dict={"ibm_job_id": ibm_program_ids[0]}, result_type=ResultType.UPLOAD_SUCCESSFUL)
        ]
        job_db_service.update_finished_job(job_core_dto.id, ibm_results, job_state=JobState.READY)

    def __run_ibm_program(self, job_core_dto: JobCoreDto):
        """EXPERIMENTAL"""
        """Run a program previously uploaded to the IBM Backend"""
        if not utils.are_experimental_features_enabled():
            raise job_db_service.return_exception_and_update_job(
                job_core_dto.id,
                ValueError(
                    "Running uploaded IBM Programs is experimental and was not fully tested. Set "
                    "ENABLE_EXPERIMENTAL_FEATURES to True to enable this feature."
                ),
            )
        logging.warn("This function is experimental and could not be fully tested yet")

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
            probabilities: dict = Pilot.calculate_probabilities(counts)
            circuit: str = job_dto.deployment.programs[i].quantum_circuit
            result_dtos.append(
                ResultDataclass(
                    circuit=circuit,
                    result_dict={"counts": counts, "probabilities": probabilities},
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
            quasi_dist: dict = Pilot.qubits_decimal_to_hex(ibm_result.quasi_dists[i], job_dto.id)
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
        supported_languages = [
            ProviderAssemblerLanguageDataclass(supported_language=language) for language in self.supported_languages
        ]
        return ProviderDataclass(with_token=True, supported_languages=supported_languages, name=self.provider_name)

    def get_standard_job_with_deployment(self, device: DeviceDataclass, user_id: Optional[str] = None) -> JobDataclass:
        language: AssemblerLanguage = AssemblerLanguage.QASM2
        programs: list[QuantumProgramDataclass] = [
            QuantumProgramDataclass(quantum_circuit=utils.get_default_qasm2_string(1), assembler_language=language),
            QuantumProgramDataclass(quantum_circuit=utils.get_default_qasm2_string(2), assembler_language=language),
        ]
        deployment = DeploymentDataclass(
            deployed_by=user_id,
            programs=programs,
            deployed_at=datetime.now(),
            name="DeploymentIBMQasmName",
        )

        return JobDataclass(
            executed_by=user_id,
            executed_on=device,
            deployment=deployment,
            progress=0,
            state=JobState.READY,
            shots=4000,
            type=JobType.RUNNER,
            started_at=datetime.now(),
            name="IBMJob",
            results=[
                ResultDataclass(
                    result_dict={
                        "counts": {"0x0": 2007, "0x3": 1993},
                        "probabilities": {"0x0": 0.50175, "0x3": 0.49825},
                    }
                )
            ],
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

    def is_device_available(self, device: DeviceDto, token: str) -> bool:
        ibm_provider: IBMProvider = IBMPilot.get_ibm_provider_and_login(token)
        try:
            ibm_provider.get_backend(device.name)
            return True
        except QiskitBackendNotFoundError:
            return False

    def get_device_data_from_provider(self, device: DeviceDto, token: str) -> dict:
        ibm_provider: IBMProvider = IBMPilot.get_ibm_provider_and_login(token)
        backend = ibm_provider.get_backend(device.name)
        config_dict: dict = vars(backend.configuration())
        # Remove some not serializable fields
        config_dict["u_channel_lo"] = None
        config_dict["_qubit_channel_map"] = None
        config_dict["_channel_qubit_map"] = None
        config_dict["_control_channels"] = None
        config_dict["gates"] = None
        return config_dict
