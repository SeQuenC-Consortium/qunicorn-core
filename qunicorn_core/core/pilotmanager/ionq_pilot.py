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

import traceback
from http import HTTPStatus
from os import environ
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple, Union, Dict

from flask.globals import current_app
import qiskit_aer
from qiskit import transpile, QuantumCircuit, QiskitError
from qiskit.primitives import Estimator as LocalEstimator
from qiskit.primitives import EstimatorResult
from qiskit.primitives import Sampler as LocalSampler
from qiskit.primitives import SamplerResult
from qiskit.providers import Backend, QiskitBackendNotFoundError
from qiskit.quantum_info import SparsePauliOp
from qiskit.result import Result
from qiskit_ibm_runtime import (
    Estimator,
    IBMRuntimeError,
    QiskitRuntimeService,
    RuntimeJob,
    Sampler,
)

from qunicorn_core.api.api_models import DeviceDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.static.qunicorn_exception import QunicornError
from qunicorn_core.util import utils



class IONQPilot(Pilot):
    """The IONQ Pilot"""

    provider_name = ProviderName.IONQ.value
    supported_languages = tuple([AssemblerLanguage.QISKIT.value])

    def execute_provider_specific(
        self, job: JobDataclass, circuits: Sequence[Tuple[QuantumProgramDataclass, Any]], token: Optional[str] = None
    ) -> JobState:
        """Execute a job of a provider specific type on a backend using a Pilot"""
        if job.id is None:
            raise QunicornError("Job has no database ID and cannot be executed!")

        if job.type == JobType.ESTIMATOR.value:
            results, state = self.__estimate(job, circuits, token=token)
        elif job.type == JobType.SAMPLER.value:
            results, state = self.__sample(job, circuits, token=token)
        elif job.type == JobType.IBM_RUNNER.value:
            results, state = self.__run_ibm_program(job, token=token)
        elif job.type == JobType.IBM_UPLOAD.value:
            results, state = self.__upload_ibm_program(job, token=token)
        else:
            raise QunicornError("No valid Job Type specified")

        job.save_results(results, state)
        return state

    def run(
        self,
        job: JobDataclass,
        circuits: Sequence[Tuple[QuantumProgramDataclass, QuantumCircuit]],
        token: Optional[str] = None,
    ) -> JobState:
        """Execute a job local using aer simulator or a real backend"""
        if job.id is None:
            raise QunicornError("Job has no database ID and cannot be executed!")
        device = job.executed_on
        if device is None:
            raise QunicornError("The job does not have any device associated!")

        backend: Backend
        if device.is_local:
            backend = qiskit_aer.Aer.get_backend("aer_simulator")
        else:
            provider = self.__get_provider_login_and_update_job(token, job)
            backend = provider.get_backend(device.name)

        programs = [p for p, _ in circuits]
        transpiled_circuits = [c for _, c in circuits]

        backend_specific_circuits = transpile(transpiled_circuits, backend)
        qiskit_job = backend.run(backend_specific_circuits, shots=job.shots)
        job.provider_specific_id = qiskit_job.job_id()
        job.save(commit=True)

        result = qiskit_job.result()
        results: list[ResultDataclass] = IBMPilot.__map_runner_results_to_dataclass(
            result, job, programs, backend_specific_circuits
        )

        # AerCircuit is not serializable and needs to be removed
        for res in results:
            if res is not None and "circuit" in res.meta:
                res.meta.pop("circuit")

        job.save_results(results, JobState.FINISHED)

        return JobState.FINISHED

    def cancel_provider_specific(self, job: JobDataclass, token: Optional[str] = None):
        """Cancel a job on an IBM backend using the IBM Pilot"""
        qiskit_job = self.__get_qiskit_job_from_qiskit_runtime(job, token=token)
        qiskit_job.cancel()
        job.state = JobState.CANCELED.value
        job.save(commit=True)
        current_app.logger.info(f"Cancel job with id {job.id} on {job.executed_on.provider.name} successful.")

    def __sample(
        self, job: JobDataclass, circuits: Sequence[Tuple[QuantumProgramDataclass, Any]], token: Optional[str] = None
    ) -> Tuple[List[ResultDataclass], JobState]:
        """Uses the Sampler to execute a job on an IBM backend using the IBM Pilot"""
        if job.executed_on.is_local:
            sampler = LocalSampler()
        else:
            backend = self.__get_qiskit_runtime_backend(job, token=token)
            sampler = Sampler(session=backend)
        job_from_ibm: RuntimeJob = sampler.run([c for _, c in circuits])
        ibm_result: SamplerResult = job_from_ibm.result()
        results = IBMPilot._map_sampler_results_to_dataclass(ibm_result, [p for p, _ in circuits], job)
        return results, JobState.FINISHED

    def __estimate(
        self, job: JobDataclass, circuits: Sequence[Tuple[QuantumProgramDataclass, Any]], token: Optional[str] = None
    ) -> Tuple[List[ResultDataclass], JobState]:
        """Uses the Estimator to execute a job on an IBM backend using the IBM Pilot"""
        observables: list = [SparsePauliOp("IY"), SparsePauliOp("IY")]
        if job.executed_on.is_local:
            estimator = LocalEstimator()
        else:
            backend = self.__get_qiskit_runtime_backend(job, token=token)
            estimator = Estimator(session=backend)
        job_from_ibm = estimator.run([c for _, c in circuits], observables=observables)
        ibm_result: EstimatorResult = job_from_ibm.result()
        results = IBMPilot._map_estimator_results_to_dataclass(ibm_result, [p for p, _ in circuits], job, "IY")
        return results, JobState.FINISHED

    def __get_qiskit_runtime_backend(self, job: JobDataclass, token: Optional[str]) -> Backend:
        """Instantiate all important configurations and updates the job_state"""

        # If the token is empty the token is taken from the environment variables.
        if not token and (t := environ.get("IBM_TOKEN")):
            token = t

        self.__get_provider_login_and_update_job(token, job.id)
        return QiskitRuntimeService().get_backend(job.executed_on.name)

    def __get_qiskit_job_from_qiskit_runtime(self, job: JobDataclass, token: Optional[str]) -> RuntimeJob:
        """Returns the job of the provider specific ID created on the given account"""

        # If the token is empty the token is taken from the environment variables.
        if not token and (t := environ.get("IBM_TOKEN")):
            token = t

        self.__get_provider_login_and_update_job(token, job.id)
        service: QiskitRuntimeService = QiskitRuntimeService()
        return service.job(job.provider_specific_id)

    @staticmethod
    def get_ibm_provider_and_login(token: Optional[str]) -> QiskitRuntimeService:
        """Save account credentials and get provider"""

        # If the token is empty the token is taken from the environment variables.
        if not token and (t := environ.get("IBM_TOKEN")):
            token = t

        # Try to save the account. Update job_dto to job_state = Error, if it is not possible
        # FIXME test and use job specific name for saving credentials??
        QiskitRuntimeService.save_account(channel="ibm_quantum", token=token, overwrite=True, name="TODO")

        return QiskitRuntimeService(channel="ibm_quantum", name="TODO")  # FIXME change name

    @staticmethod
    def __get_provider_login_and_update_job(token: str, job: JobDataclass) -> QiskitRuntimeService:
        """Save account credentials, get provider and update job_dto to job_state = Error, if it is not possible"""

        try:
            return IBMPilot.get_ibm_provider_and_login(token)
        except Exception as exception:
            job.save_error(exception)
            raise QunicornError(type(exception).__name__ + ": " + str(exception.args), HTTPStatus.UNAUTHORIZED)

    @staticmethod
    def __get_file_path_to_resources(file_name) -> str:
        # TODO: resources should be placed relative to the app instance folder!!! (or in the database)
        working_directory_path = Path(".").resolve()
        file_path = working_directory_path / "resources" / "upload_files" / file_name
        return str(file_path)

    def __upload_ibm_program(self, job: JobDataclass, token: Optional[str]) -> Tuple[List[ResultDataclass], JobState]:
        """EXPERIMENTAL -- Upload and then run a quantum program on the QiskitRuntimeService"""

        self.check_if_env_variable_true_for_experimental(job)

        service = self.__get_runtime_service(job, token=token)
        ibm_program_ids = []
        for program in job.deployment.programs:
            python_file_path = self.__get_file_path_to_resources(program.python_file_path)
            python_file_metadata_path = self.__get_file_path_to_resources(program.python_file_metadata)
            ibm_program_ids.append(service.upload_program(python_file_path, python_file_metadata_path))

        job.type = JobType.IBM_RUNNER.value
        job.save(commit=True)
        result_type: ResultType = ResultType.UPLOAD_SUCCESSFUL
        ibm_results = [ResultDataclass(data={"ibm_job_id": ibm_program_ids[0]}, result_type=result_type)]
        return ibm_results, JobState.READY

    def __run_ibm_program(self, job: JobDataclass, token: Optional[str]) -> Tuple[List[ResultDataclass], JobState]:
        """EXPERIMENTAL -- Run a program previously uploaded to the IBM Backend"""
        self.check_if_env_variable_true_for_experimental(job)

        service = self.__get_runtime_service(job, token=token)
        options_dict: Optional[dict] = None  # job.ibm_file_options  # FIXME
        input_dict: Optional[dict] = None  # job.ibm_file_inputs  # FIXME
        ibm_job_id = job.results[0].result_dict["ibm_job_id"]  # FIXME

        try:
            result: RuntimeJob = service.run(ibm_job_id, inputs=input_dict, options=options_dict).result()
        except IBMRuntimeError as exception:
            job.save_error(exception)
            raise QunicornError(type(exception).__name__, HTTPStatus.INTERNAL_SERVER_ERROR)

        # use assert to pacify linter for now...
        assert result  # FIXME: actually use result object
        ibm_results = [ResultDataclass()]  # FIXME: map result to list of ResultDataclass

        return ibm_results, JobState.FINISHED

    @staticmethod
    def check_if_env_variable_true_for_experimental(job: JobDataclass):
        """EXPERIMENTAL -- Raise an error if the experimental env variable is not true and logs a warning"""

        exception_str: str = (
            "Running uploaded IBM Programs is experimental and has not been fully tested yet."
            "Set ENABLE_EXPERIMENTAL_FEATURES to True to enable this feature."
        )

        if not utils.is_experimental_feature_enabled():
            exception: Exception = QunicornError(exception_str, HTTPStatus.NOT_IMPLEMENTED)
            job.save_error(exception)
            raise exception

        current_app.logger.warn("This function is experimental and could not be fully tested yet")

    @staticmethod
    def __get_runtime_service(job: JobDataclass, token: Optional[str]) -> QiskitRuntimeService:
        # If the token is empty the token is taken from the environment variables.
        if not token and (t := environ.get("IBM_TOKEN")):
            token = t

        service = QiskitRuntimeService(token=None, channel=None, filename=None, name=None)
        service.save_account(token=token, channel="ibm_quantum", overwrite=True)
        return service

    @staticmethod
    def __map_runner_results_to_dataclass(
        ibm_result: Result,
        job: JobDataclass,
        programs: Sequence[QuantumProgramDataclass],
        circuits: List[QuantumCircuit] = None,
    ) -> list[ResultDataclass]:
        results: list[ResultDataclass] = []

        try:
            binary_counts = ibm_result.get_counts()
        except QiskitError:
            binary_counts = [None]

        if isinstance(binary_counts, dict):
            binary_counts = [binary_counts]

        for i, result in enumerate(ibm_result.results):
            metadata = result.to_dict()
            metadata["format"] = "hex"
            classical_registers_metadata = []

            for reg in reversed(circuits[i].cregs):
                # FIXME: don't append registers that are not measured
                classical_registers_metadata.append({"name": reg.name, "size": reg.size})

            metadata["registers"] = classical_registers_metadata
            metadata.pop("data")
            metadata.pop("circuit", None)

            hex_counts = IBMPilot._binary_counts_to_hex(binary_counts[i])

            results.append(
                ResultDataclass(
                    program=programs[i],
                    result_type=ResultType.COUNTS,
                    data=hex_counts if hex_counts else {"": 0},
                    meta=metadata,
                )
            )

            probabilities: dict = Pilot.calculate_probabilities(hex_counts) if hex_counts else {"": 0}

            results.append(
                ResultDataclass(
                    program=programs[i],
                    result_type=ResultType.PROBABILITIES,
                    data=probabilities,
                    meta=metadata,
                )
            )
        return results

    @staticmethod
    def _binary_counts_to_hex(binary_counts: Dict[str, int] | None) -> Dict[str, int] | None:
        if binary_counts is None:
            return None

        hex_counts = {}

        for k, v in binary_counts.items():
            hex_registers = []

            for binary_register in k.split():
                hex_registers.append(f"0x{int(binary_register, 2):x}")

            hex_sample = " ".join(hex_registers)

            hex_counts[hex_sample] = v

        return hex_counts

    @staticmethod
    def _map_estimator_results_to_dataclass(
        ibm_result: EstimatorResult, programs: Sequence[QuantumProgramDataclass], job: JobDataclass, observer: str
    ) -> list[ResultDataclass]:
        result_dtos: list[ResultDataclass] = []
        for i in range(len(ibm_result.metadata)):  # FIXME test this
            value: float = ibm_result.values[i]
            variance: float = ibm_result.metadata[i]["variance"]
            result_dtos.append(
                ResultDataclass(
                    program=programs[i],
                    result_dict={"value": str(value), "variance": str(variance)},
                    data=ResultType.VALUE_AND_VARIANCE,
                    meta={"observer": f"SparsePauliOp-{observer}"},
                )
            )
        return result_dtos

    @staticmethod
    def _map_sampler_results_to_dataclass(
        ibm_result: SamplerResult, programs: Sequence[QuantumProgramDataclass], job: JobDataclass
    ) -> list[ResultDataclass]:
        results: list[ResultDataclass] = []
        contains_errors = False
        for i in range(len(ibm_result.quasi_dists)):
            try:
                results.append(
                    ResultDataclass(
                        program=programs[i],
                        data=Pilot.qubits_integer_to_hex(ibm_result.quasi_dists[i]),
                        result_type=ResultType.QUASI_DIST,
                    )
                )
            except QunicornError as err:
                exception_message: str = str(err)
                stack_trace: str = "".join(traceback.format_exception(err))
                results.append(
                    ResultDataclass(
                        result_type=ResultType.ERROR.value,
                        job=job,
                        program=programs[i],
                        data={"exception_message": exception_message},
                        meta={"stack_trace": stack_trace},
                    )
                )
                contains_errors = True
        job.save_results(results, JobState.ERROR if contains_errors else JobState.FINISHED)
        return results

    def get_standard_provider(self) -> ProviderDataclass:
        found_provider = ProviderDataclass.get_by_name(self.provider_name)
        if not found_provider:
            found_provider = ProviderDataclass(with_token=True, name=self.provider_name)
            found_provider.supported_languages = list(self.supported_languages)
            found_provider.save()  # make sure that the provider will be committed to DB
        return found_provider

    def get_standard_job_with_deployment(self, device: DeviceDataclass) -> JobDataclass:
        circuit: str = (
            "circuit = QuantumCircuit(2, 2);circuit.h(0); circuit.cx(0, 1);circuit.measure(0, 0);circuit.measure(1, 1)"
        )
        return self.create_default_job_with_circuit_and_device(device, circuit, assembler_language="QISKIT-PYTHON")

    def save_devices_from_provider(self, token: Optional[str]):
        ibm_provider: QiskitRuntimeService = IBMPilot.get_ibm_provider_and_login(token)
        all_devices = ibm_provider.backends()

        provider: Optional[ProviderDataclass] = self.get_standard_provider()

        # First save all devices from the cloud service
        for ibm_device in all_devices:
            found_device = DeviceDataclass.get_by_name(ibm_device.name, provider)
            if not found_device:
                found_device = DeviceDataclass(
                    name=ibm_device.name,
                    num_qubits=-1 if ibm_device.name.__contains__("stabilizer") else ibm_device.num_qubits,
                    is_simulator=ibm_device.name.__contains__("simulator"),
                    is_local=False,
                    provider=provider,
                )
            else:
                found_device.num_qubits = -1 if ibm_device.name.__contains__("stabilizer") else ibm_device.num_qubits
                found_device.is_simulator = ibm_device.name.__contains__("simulator")
                found_device.is_local = False
            found_device.save()

        found_aer_device = DeviceDataclass.get_by_name("aer_simulator", provider)
        if not found_aer_device:
            # Then add the local simulator
            found_aer_device = DeviceDataclass(
                name="aer_simulator",
                num_qubits=-1,
                is_simulator=True,
                is_local=True,
                provider=provider,
            )
        else:
            found_aer_device.num_qubits = -1
            found_aer_device.is_simulator = True
            found_aer_device.is_local = True
        found_aer_device.save(commit=True)

    def is_device_available(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> bool:
        ibm_provider: QiskitRuntimeService = IBMPilot.get_ibm_provider_and_login(token)
        if device.is_simulator:
            return True
        try:
            ibm_provider.get_backend(device.name)
            return True
        except QiskitBackendNotFoundError:
            return False

    def get_device_data_from_provider(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> dict:
        ibm_provider: QiskitRuntimeService = IBMPilot.get_ibm_provider_and_login(token)
        backend = ibm_provider.get_backend(device.name)
        config_dict: dict = vars(backend.configuration())
        # Remove some not serializable fields
        config_dict["u_channel_lo"] = None
        config_dict["_qubit_channel_map"] = None
        config_dict["_channel_qubit_map"] = None
        config_dict["_control_channels"] = None
        config_dict["gates"] = None
        return config_dict
