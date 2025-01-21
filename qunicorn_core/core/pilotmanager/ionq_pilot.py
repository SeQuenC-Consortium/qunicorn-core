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


from itertools import groupby
from typing import List, Optional, Sequence, Dict

from flask.globals import current_app


#ionq imports
from qiskit_ionq import IonQProvider
from qiskit import QuantumCircuit, transpile, QiskitError
from qiskit.result import Result

from qunicorn_core.core.pilotmanager.base_pilot import Pilot, PilotJob, PilotJobResult
from qunicorn_core.db.db import DB
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.job_state import TransientJobStateDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.static.qunicorn_exception import QunicornError
from qunicorn_core.util import utils

#devices IONQ Pilot: 'simulator', qpu.forte-1 , qpu.aria-1, qpu.aria-2
#ionq uses Qiskit as SDK 


class IONQPilot(Pilot):
    """The IonQ Pilot"""

    provider_name = ProviderName.IONQ.value
    supported_languages = tuple([AssemblerLanguage.QISKIT.value])

    def run(self, jobs: Sequence[PilotJob], token: Optional[str] = None):

        """Execute a job local using ionq_simulator"""
        batched_jobs = [(db_job, list(pilot_jobs)) for db_job, pilot_jobs in groupby(jobs, lambda j: j.job)]

        for db_job, pilot_jobs in batched_jobs:
            device = db_job.executed_on
            if device is None:
                db_job.save_error(QunicornError("The job does not have any device associated!"))
                continue  # one job failing should not affect other jobs
            else:
                if IONQPilot.is_device_available(device, token):
                    provider = IonQProvider(token)
                    backend = provider.backend(device.name) #possible are simulator or ionq
                else:
                    current_app.logger.info(f"Device {device.name} is not available")


            pilot_jobs = list(pilot_jobs)

            backend_specific_circuits = transpile([j.circuit for j in pilot_jobs], backend)
            qiskit_job = backend.run(backend_specific_circuits, shots=db_job.shots)

            job_state: Optional[TransientJobStateDataclass] = None

            for state in db_job._transient:
                if state.program is not None and isinstance(state.data, dict):
                    if state.data.get("type") == "IONQ":
                        job_state = state
                        break
            else:
                job_state = TransientJobStateDataclass(db_job, data={"type": "IONQ"})

            provider_specific_ids = job_state.data.get("provider_ids", [])
            provider_specific_ids.append(qiskit_job.job_id())
            job_state.data = dict(job_state.data) | {"provider_ids": provider_specific_ids}
            job_state.save()

            db_job.state = JobState.RUNNING.value
            db_job.save(commit=True)

            result = qiskit_job.result()
            mapped_results: list[Sequence[PilotJobResult]] = IONQPilot.__map_runner_results(
                result, backend_specific_circuits
            )

            for pilot_results, pilot_job in zip(mapped_results, pilot_jobs):
                self.save_results(pilot_job, pilot_results)
            DB.session.commit()

    def execute_provider_specific(self, jobs: Sequence[PilotJob], job_type: str, token: Optional[str] = None):
        """Execute a job of a provider specific type on a backend using a Pilot"""
        raise QunicornError("No valid Job Type specified. IonQ does not support provider specific jobs")

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
        provider = IonQProvider(token)
        backends = provider.backends()
        for ionq_device in backends:
            backend = provider.get_backend(ionq_device.name)
            config = backend.configuration()
            device_data = DeviceDataclass.get_by_name(ionq_device.name,provider)
            if not found_device:
                found_device = DeviceDataclass(
                    name=ionq_device.name,
                    num_qubits=config.n_qubits,
                    is_simulator=ionq_device.name.__contains__("simulator"),
                    is_local=False,
                    provider=provider,
                )
            else:
                found_device.num_qubits = config.n_qubits
                found_device.is_simulator = ionq_device.name.__contains__("simulator")
                found_device.is_local = False
            found_device.save()

    def is_device_available(self, device, token):
        provider = IonQProvider(token)
        backend = provider.get_backend(device.name)
        status = backend.status()
        return status == "online"
    
    def get_device_data_from_provider(self, device, token):
        provider = IonQProvider(token)
        backend = provider.get_backend(device.name)
        config_dict: dict = vars(backend.configuration())
        return config_dict

    def cancel_provider_specific(self, job: JobDataclass, token: Optional[str] = None):
        provider = IonQProvider(token)
        ionq_job = provider.get_job(job.id)
        ionq_job.cancel()
        job.state = JobState.CANCELED.value
        job.save(commit=True)
        current_app.logger.info(f"Cancel job with id {job.id} on {job.executed_on.provider.name} successful.")

    @staticmethod
    def __map_runner_results(
        ionq_result: Result, circuits: List[QuantumCircuit] = None
    ) -> list[Sequence[PilotJobResult]]:
        results: list[Sequence[PilotJobResult]] = []

        try:
            binary_counts = ionq_result.get_counts()
        except QiskitError:
            binary_counts = [None]

        if isinstance(binary_counts, dict):
            binary_counts = [binary_counts]

        for i, result in enumerate(ionq_result.results):
            pilot_results: list[PilotJobResult] = []
            results.append(pilot_results)

            metadata = result.to_dict()
            metadata["format"] = "hex"
            classical_registers_metadata = []

            for reg in reversed(circuits[i].cregs):
                # FIXME: don't append registers that are not measured
                classical_registers_metadata.append({"name": reg.name, "size": reg.size})

            metadata["registers"] = classical_registers_metadata
            metadata.pop("data")
            metadata.pop("circuit", None)

            hex_counts = IONQPilot._binary_counts_to_hex(binary_counts[i])

            pilot_results.append(
                PilotJobResult(
                    result_type=ResultType.COUNTS,
                    data=hex_counts if hex_counts else {"": 0},
                    meta=metadata,
                )
            )

            probabilities: dict = utils.calculate_probabilities(hex_counts) if hex_counts else {"": 0}

            pilot_results.append(
                PilotJobResult(
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