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
from qiskit_ionq import IonQProvider  ##my
from qiskit_ionq import IonQProvider, ErrorMitigation  ##my

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
        """Execute a job of a provider specific type on a backend using a pilot"""
        if job.id is None:
            raise QunicornError("Job has no database ID and cannot be executed!")
        raise QunicornError("No valid Job Type specified")

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
            
            # Check if IonQ is the provider
            if isinstance(provider, IonQProvider):  # Ensure it's IonQ provider
                backend = provider.get_backend(device.name)  # IonQ backend name
            else:
                backend = provider.get_backend(device.name)

        programs = [p for p, _ in circuits]
        transpiled_circuits = [c for _, c in circuits]

        backend_specific_circuits = transpile(transpiled_circuits, backend)
        qiskit_job = backend.run(backend_specific_circuits, shots=job.shots)
        job.provider_specific_id = qiskit_job.job_id()
        job.save(commit=True)

        result = qiskit_job.result()
        results: list[ResultDataclass] = IONQPilot.__map_runner_results_to_dataclass(
            result, job, programs, backend_specific_circuits
        )

        # AerCircuit is not serializable and needs to be removed
        for res in results:
            if res is not None and "circuit" in res.meta:
                res.meta.pop("circuit")

        job.save_results(results, JobState.FINISHED)

        return JobState.FINISHED

    def cancel_provider_specific(self, job: JobDataclass, token: Optional[str] = None):
        """Cancel a job on an IONQ backend using the IONQ Pilot"""
        qiskit_job = self.__get_ionq_job_from_provider(job, token=token)
        qiskit_job.cancel()
        job.state = JobState.CANCELED.value
        job.save(commit=True)
        current_app.logger.info(f"Cancel job with id {job.id} on {job.executed_on.provider.name} successful.")


    def __get_ionq_job_from_provider(self, job: JobDataclass, token: Optional[str]) -> IonQJob:
        """Returns the IonQ job created on the given account"""
        
        # If the token is empty, the token is taken from the environment variables.
        if not token and (t := environ.get("IONQ_TOKEN")):
            token = t

        # Ensure the provider is logged in and up-to-date
        provider = self.__get_provider_login_and_update_job(token, job)

        # Get the IonQ backend (make sure the job's provider ID is valid)
        ionq_backend = provider.get_backend(job.executed_on.provider.name)

        # Fetch the IonQ job using the provider-specific job ID
        ionq_job = ionq_backend.job(job.provider_specific_id)
        return ionq_job

    @staticmethod
    def get_ionq_provider_and_login(token: Optional[str]) -> IonQProvider:
        """Save account credentials and get Ionq provider"""

        # If the token is empty the token is taken from the environment variables.
        if not token and (t := environ.get("IONQ_TOKEN")):
            token = t

        # Try to log in and get the IonQ provider
        # The IonQ provider uses the API token to authenticate
        if token:
            # This assumes you have an IonQ API token saved or provided via env var or function input
            provider = IonQProvider(token=token)
        else:
            raise QunicornError("IonQ API token is missing", HTTPStatus.UNAUTHORIZED)

        return provider

    @staticmethod
    def __get_provider_login_and_update_job(token: str, job: JobDataclass) -> IonQProvider:
        """Save account credentials, get Ionq provider and update job_dto to job_state = Error, if it is not possible"""

        try:
            return IONQPilot.get_ionq_provider_and_login(token)
        except Exception as exception:
            job.save_error(exception)
            raise QunicornError(type(exception).__name__ + ": " + str(exception.args), HTTPStatus.UNAUTHORIZED)



    @staticmethod
    def __map_runner_results_to_dataclass(
        ionq_result: dict,  # Assuming IonQ returns a dictionary-like object
        job: JobDataclass,
        programs: Sequence[QuantumProgramDataclass],
        circuits: List[QuantumCircuit] = None,
    ) -> list[ResultDataclass]:
        results: list[ResultDataclass] = []

        # Extract counts from IonQ result, assuming the structure is different from IBM
        try:
            counts = ionq_result.get("counts", {})
        except KeyError:
            counts = {}

        if isinstance(counts, dict):
            counts = [counts]  # Convert to list if it's a single dict

        for i, result in enumerate(ionq_result.get("results", [])):
            metadata = result.get("metadata", {})
            metadata["format"] = "hex"
            classical_registers_metadata = []

            # Collect metadata about the classical registers
            for reg in reversed(circuits[i].cregs):
                classical_registers_metadata.append({"name": reg.name, "size": reg.size})

            metadata["registers"] = classical_registers_metadata
            metadata.pop("data", None)  # Remove "data" if it exists
            metadata.pop("circuit", None)  # Remove "circuit" if it exists

            # Convert counts to hexadecimal format (IonQ might require a custom implementation here)
            hex_counts = IONQPilot._binary_counts_to_hex(counts[i]) if counts else {}

            # Append the counts result
            results.append(
                ResultDataclass(
                    program=programs[i],
                    result_type=ResultType.COUNTS,
                    data=hex_counts if hex_counts else {"": 0},
                    meta=metadata,
                )
            )

            # Calculate probabilities (assuming the same structure for probabilities calculation)
            probabilities = Pilot.calculate_probabilities(hex_counts) if hex_counts else {"": 0}

            # Append the probabilities result
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
        ionq_result: dict,  # IonQ Estimator result, assumed to be a dictionary
        programs: Sequence[QuantumProgramDataclass],
        job: JobDataclass,
        observer: str
    ) -> list[ResultDataclass]:
        result_dtos: list[ResultDataclass] = []
        
        # Assuming ionq_result['results'] contains the list of estimation results
        for i, result in enumerate(ionq_result.get("results", [])):
            value: float = result.get("value", 0.0)  # Get the estimated value
            variance: float = result.get("variance", 0.0)  # Get the variance
            
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
        ionq_result: dict,  # IonQ Sampler result, assumed to be a dictionary
        programs: Sequence[QuantumProgramDataclass],
        job: JobDataclass
    ) -> list[ResultDataclass]:
        results: list[ResultDataclass] = []
        contains_errors = False

        # Assuming ionq_result['samples'] contains the list of sample distributions
        for i, sample in enumerate(ionq_result.get("samples", [])):
            try:
                # Convert the sample data (depending on IonQ's format, you might need custom logic here)
                # For instance, if IonQ returns a dictionary of counts or measurements, you might need to convert it to a hex string
                hex_result = Pilot.qubits_integer_to_hex(sample)  # Assuming this function can handle IonQ data structure

                results.append(
                    ResultDataclass(
                        program=programs[i],
                        data=hex_result,
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
        # IonQ doesn't use Qiskit for circuit creation, so adapt accordingly
        circuit: str = "circuit = IonQQuantumCircuit(2);circuit.h(0); circuit.cx(0, 1);circuit.measure(0, 0);circuit.measure(1, 1)"
        return self.create_default_job_with_circuit_and_device(device, circuit, assembler_language="IONQ-PYTHON")

    def save_devices_from_provider(self, token: Optional[str]):
        ionq_provider: IonQService = self.get_ionq_provider_and_login(token)
        all_devices = ionq_provider.get_devices()

        provider: Optional[ProviderDataclass] = self.get_standard_provider()

        # First save all devices from IonQ
        for ionq_device in all_devices:
            found_device = DeviceDataclass.get_by_name(ionq_device.name, provider)
            if not found_device:
                found_device = DeviceDataclass(
                    name=ionq_device.name,
                    num_qubits=ionq_device.num_qubits,
                    is_simulator=ionq_device.is_simulator,
                    is_local=False,
                    provider=provider,
                )
            else:
                found_device.num_qubits = ionq_device.num_qubits
                found_device.is_simulator = ionq_device.is_simulator
                found_device.is_local = False
            found_device.save()

        # Handle local simulators, if applicable
        found_local_device = DeviceDataclass.get_by_name("ionq_local_simulator", provider)
        if not found_local_device:
            found_local_device = DeviceDataclass(
                name="ionq_local_simulator",
                num_qubits=-1,
                is_simulator=True,
                is_local=True,
                provider=provider,
            )
        found_local_device.save(commit=True)

    def is_device_available(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> bool:
        ionq_provider: IonQService = self.get_ionq_provider_and_login(token)
        if device.is_simulator:
            return True
        try:
            ionq_provider.get_device(device.name)
            return True
        except Exception:  # Handle IonQ-specific error
            return False

    def get_device_data_from_provider(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> dict:
        ionq_provider: IonQService = self.get_ionq_provider_and_login(token)
        backend = ionq_provider.get_device(device.name)
        config_dict: dict = backend.configuration()  # Adjust this based on IonQ's API response structure
        # Remove non-serializable fields if necessary
        config_dict["some_non_serializable_field"] = None  # Example placeholder
        return config_dict

    def get_ionq_provider_and_login(self, token: Optional[str]) -> IonQService:
        """Log in to IonQ and return the provider object."""
        if not token:
            raise ValueError("Token is required for IonQ authentication.")
        ionq_service = IonQService(token=token)
        return ionq_service