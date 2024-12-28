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
from itertools import groupby
from typing import List, Optional, Sequence, Union

from flask.globals import current_app
from braket.devices import LocalSimulator
from braket.ir.openqasm import Program
from braket.tasks import GateModelQuantumTaskResult
from braket.tasks.local_quantum_task_batch import LocalQuantumTaskBatch

from qunicorn_core.api.api_models.device_dtos import DeviceDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot, PilotJob, PilotJobResult
from qunicorn_core.db.db import DB
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.static.qunicorn_exception import QunicornError


class IONQPilot(Pilot):
    """The IONQ Pilot"""

    provider_name = ProviderName.IONQ.value
    supported_languages = tuple([AssemblerLanguage.QISKIT.value])

    def run(self, jobs: Sequence[PilotJob], token: Optional[str] = None):
        """Execute the job on a local simulator and saves results in the database"""
        if any(not j.job.executed_on or not j.job.executed_on.is_local for j in jobs):
            raise QunicornError("Device not found, device needs to be local for IONQ")

        batches = [(k, list(j)) for k, j in groupby(jobs, key=lambda j: j.job.shots)]

        for shots, jobs in batches:
            # Since QASM is stored as a string, it needs to be converted to a QASM program before execution
            # FIXME: support circuits where not all qubits have gates
            preprocessed_circuits = [
                (Program(source=j.circuit) if isinstance(j.circuit, str) else j.circuit) for j in jobs
            ]

            quantum_tasks: LocalQuantumTaskBatch = LocalSimulator().run_batch(preprocessed_circuits, shots=shots)

            results = IONQPilot._map_ionq_results(quantum_tasks.results())
            for result, job in zip(results, jobs):
                self.save_results(job, result, commit=False)
        DB.session.commit()

    def execute_provider_specific(self, jobs: Sequence[PilotJob], job_type: str, token: Optional[str] = None):
        """Execute a job of a provider specific type on a backend using a pilot"""
        raise QunicornError("No valid Job Type specified")

    def cancel_provider_specific(self, job_dto):
        current_app.logger.warning(
            f"Cancel job with id {job_dto.id} on {job_dto.executed_on.provider.name} failed."
            f"Canceling while in execution not supported for IONQ Jobs"
        )
        raise QunicornError("Canceling not supported on IONQ devices")

    @staticmethod
    def _map_ionq_results(ionq_results: list[GateModelQuantumTaskResult]) -> List[List[PilotJobResult]]:
        results: List[List[PilotJobResult]] = []

        for result in ionq_results:
            job_results: List[PilotJobResult] = []
            metadata = result.additional_metadata.dict()
            metadata["format"] = "hex"

            most_common_bitstring: str = result.measurement_counts.most_common(1)[0][0]
            metadata["registers"] = [
                {"name": "", "size": len(most_common_bitstring)}
            ]  # FIXME: support multiple registers

            try:
                job_results.append(
                    PilotJobResult(
                        data=Pilot.qubit_binary_string_to_hex(result.measurement_counts, reverse_qubit_order=True),
                        meta=metadata,
                        result_type=ResultType.COUNTS,
                    )
                )
                job_results.append(
                    PilotJobResult(
                        data=Pilot.qubit_binary_string_to_hex(
                            result.measurement_probabilities, reverse_qubit_order=True
                        ),
                        meta=metadata,
                        result_type=ResultType.PROBABILITIES,
                    )
                )
                results.append(job_results)

            except QunicornError as err:
                exception_message: str = str(err)
                stack_trace: str = "".join(traceback.format_exception(err))
                results.append(
                    [
                        PilotJobResult(
                            result_type=ResultType.ERROR,
                            data={"exception_message": exception_message},
                            meta={"stack_trace": stack_trace},
                        )
                    ]
                )
        return results

    def get_standard_job_with_deployment(self, device: DeviceDataclass) -> JobDataclass:
        return self.create_default_job_with_circuit_and_device(device, "Circuit().h(0).cnot(0, 1)")

    def save_devices_from_provider(self, token: Optional[str]):
        raise QunicornError("IONQ Pilot cannot fetch Devices from IONQ API, because there is no Cloud Access.")

    def get_standard_provider(self) -> ProviderDataclass:
        found_provider = ProviderDataclass.get_by_name(self.provider_name)
        if not found_provider:
            found_provider = ProviderDataclass(
                with_token=False,
                name=self.provider_name,
            )
            found_provider.supported_languages = list(self.supported_languages)
            found_provider.save()
        return found_provider

    def is_device_available(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> bool:
        current_app.logger.info("IONQ local simulator is always available")
        return True