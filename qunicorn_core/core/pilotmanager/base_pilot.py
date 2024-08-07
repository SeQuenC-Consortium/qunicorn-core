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
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple, Union, Generator

from celery.states import PENDING

from qunicorn_core.api.api_models.device_dtos import DeviceDto
from qunicorn_core.celery import CELERY
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.qunicorn_exception import QunicornError
from qunicorn_core.util.utils import is_running_asynchronously


class Pilot:
    """Base class for Pilots"""

    provider_name: str
    supported_languages: Sequence[str]

    def run(
        self, job: JobDataclass, circuits: Sequence[Tuple[QuantumProgramDataclass, Any]], token: Optional[str] = None
    ) -> JobState:
        """Run a job of type RUNNER on a backend using a Pilot"""
        raise NotImplementedError()

    def execute_provider_specific(
        self, job: JobDataclass, circuits: Sequence[Tuple[QuantumProgramDataclass, Any]], token: Optional[str] = None
    ) -> JobState:
        """Execute a job of a provider specific type on a backend using a Pilot"""
        raise NotImplementedError()

    def get_standard_provider(self) -> ProviderDataclass:
        """Create the standard ProviderDataclass Object for the pilot and return it"""
        raise NotImplementedError()

    def get_standard_job_with_deployment(self, device: DeviceDataclass) -> JobDataclass:
        """Create the standard ProviderDataclass Object for the pilot and return it"""
        raise NotImplementedError()

    def save_devices_from_provider(self, token: Optional[str]):
        """Access the devices from the cloud service of the provider, to update the current device list of qunicorn"""
        raise NotImplementedError()

    def is_device_available(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> bool:
        """Check if a device is available for a user"""
        raise NotImplementedError()

    def get_device_data_from_provider(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> dict:
        """Get device data for a specific device from the provider"""
        raise NotImplementedError()

    def execute(
        self, job: JobDataclass, circuits: Sequence[Tuple[QuantumProgramDataclass, Any]], token: Optional[str] = None
    ) -> JobState:
        """Execute a job on a backend using a Pilot"""

        if job.type == JobType.RUNNER.value:
            return self.run(job, circuits, token=token)
        else:
            return self.execute_provider_specific(job, circuits, token=token)

    def cancel(self, job_id: Optional[int], user_id: Optional[str], token: Optional[str] = None):
        """Cancel the execution of a job, locally or if that is not possible at the backend"""
        if job_id is None:
            raise QunicornError("A Job without an ID cannot be cancelled!", HTTPStatus.BAD_REQUEST)
        if not is_running_asynchronously():
            raise QunicornError("Canceling a job is not possible in synchronous mode", HTTPStatus.NOT_IMPLEMENTED)
        job = JobDataclass.get_by_id_authenticated_or_404(job_id, user_id)
        if job.state == JobState.READY.value and not job.celery_id == "synchronous" and job.celery_id is not None:
            res = CELERY.AsyncResult(job.celery_id)
            if res.status == PENDING:
                res.revoke()
                job.state = JobState.CANCELED.value
                job.save(commit=True)
        elif job.state == JobState.RUNNING:
            self.cancel_provider_specific(job, token=token)
        else:
            raise QunicornError(f"Job is in invalid state for canceling: {job.state}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def cancel_provider_specific(self, job: JobDataclass, token: Optional[str] = None):
        """Cancel execution of a job at the corresponding backend"""
        raise NotImplementedError()

    def has_same_provider(self, provider_name: str) -> bool:
        """Check if the provider name is the same as the pilot provider name"""
        return self.provider_name == provider_name

    def get_standard_devices(self) -> Tuple[list[DeviceDataclass], DeviceDataclass]:
        """Get all devices from the provider"""

        root_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = f"{self.provider_name.lower()}_standard_devices.json"
        file_path = Path(root_dir) / "pilot_resources" / file_name
        with file_path.open("rt", encoding="utf-8") as f:
            all_devices = json.load(f)

        provider: ProviderDataclass = self.get_standard_provider()
        devices_without_default: list[DeviceDataclass] = []
        default_device: DeviceDataclass | None = None
        for device_json in all_devices["all_devices"]:
            name = device_json["name"]
            found_device = DeviceDataclass.get_by_name(name, provider)
            if not found_device:
                found_device = DeviceDataclass(provider=provider, **device_json)
            else:
                found_device.num_qubits = device_json.get("num_qubits", found_device.num_qubits)
                found_device.is_local = device_json.get("is_local", found_device.is_local)
                found_device.is_simulator = device_json.get("is_simulator", found_device.is_simulator)
            found_device.save()
            if found_device.is_local and default_device is None:
                default_device = found_device
            else:
                devices_without_default.append(found_device)

        if default_device is None:
            raise QunicornError("No default device found for provider {}".format(self.provider_name))

        return devices_without_default, default_device

    @staticmethod
    def qubits_integer_to_hex(qubits_as_integers: dict) -> dict:
        """To make sure that the qubits in the counts or probabilities are in
        hex string format and not in decimal integer format.

        @param qubits_as_integers: example: { 3: 1234 }
        @return: example: { "0x3": 1234 }
        """
        try:
            return dict([(hex(k), v) for k, v in qubits_as_integers.items()])
        except Exception:
            raise QunicornError("Could not convert decimal-results to hex")

    @staticmethod
    def qubit_binary_string_to_hex(qubits_in_binary: dict, reverse_qubit_order: bool = False) -> dict:
        """To make sure that the qubits in the counts or probabilities are in hex format with registers and not in
        binary string format with registers

        @param qubits_in_binary: example: { "010 1": 1234 }
        @param reverse_qubit_order: whether to reverse the order of the qubits
        @return: example: { "0x2 0x1": 1234 }
        """

        try:
            hex_result = {}

            for bitstring, v in qubits_in_binary.items():
                registers: List[str] = bitstring.split()
                hex_registers = []

                for reg in registers:
                    if reverse_qubit_order:
                        reg = reg[::-1]

                    hex_registers.append(f"0x{int(reg, 2):x}")

                hex_string = " ".join(hex_registers)
                hex_result[hex_string] = v

            return hex_result

        except Exception:
            raise QunicornError("Could not convert binary-results to hex")

    @staticmethod
    def qubit_hex_string_to_binary(
        qubits_in_hex: dict, registers: List[int], reverse_qubit_order: bool = False
    ) -> dict:
        """To make sure that the qubits in the counts or probabilities are in binary format with registers and not in
        hex string format without registers

        @param qubits_in_hex: example: { "0x5": 1234 }
        @param registers: size of the registers, example: [3, 1]
        @param reverse_qubit_order: whether to reverse the order of the qubits in the individual registers
        @return: example: { "010 1": 1234 }
        """

        try:
            hex_result = {}
            max_len = sum(registers)

            for hex_string, v in qubits_in_hex.items():
                binary_string = f"{int(hex_string, 16):0{max_len}b}"
                binary_string = binary_string[-max_len:]

                def sliced(binary) -> Generator[str]:
                    start = 0

                    for reg in registers:
                        end = start + reg
                        bin_register = binary[start:end]

                        if reverse_qubit_order:
                            bin_register = bin_register[::-1]

                        yield bin_register
                        start = end

                binary_registers = " ".join(sliced(binary_string))

                hex_result[binary_registers] = v

            return hex_result

        except Exception:
            raise QunicornError("Could not convert binary-results to hex")

    @staticmethod
    def calculate_probabilities(counts: dict) -> dict:
        """Calculates the probabilities from the counts, probability = counts / total_counts"""

        total_counts = sum(counts.values())
        probabilities = {}
        for key, value in counts.items():
            probabilities[key] = value / total_counts
        return probabilities

    def create_default_job_with_circuit_and_device(
        self, device: DeviceDataclass, circuit: str, assembler_language: Optional[str] = None
    ) -> JobDataclass:
        """
        Method to create a default job for a pilot with one given circuit and device.
        This method always takes the first supported Language of the pilot and assigns it to the program.
        The Deployment and Job Name will be generated from the ProviderName and SupportedLanguage of the Pilot.
        """
        if assembler_language is None:
            assembler_language = self.supported_languages[0]
        program = QuantumProgramDataclass(quantum_circuit=circuit, assembler_language=assembler_language)
        name: str = f"{assembler_language}_Deployment"
        deployment = DeploymentDataclass(deployed_by=None, programs=[program], deployed_at=datetime.now(), name=name)

        counts: dict = {"0x0": 2007, "0x3": 1993}
        # probs: dict = {"0x0": 0.50175, "0x3": 0.49825}  # TODO: add as additional result
        job_name = device.provider.name + "Job"
        return JobDataclass(
            executed_by=None,
            executed_on=device,
            deployment=deployment,
            progress=0,
            state=JobState.READY.value,
            shots=4000,
            type=JobType.RUNNER.value,
            started_at=datetime.now(),
            name=job_name,
            results=[
                ResultDataclass(
                    data=counts,
                    meta={"format": "hex", "shots": 4000, "registers": {"name": "output", "size": 2}},
                    result_type="COUNTS",
                )
            ],
        )
