# Copyright 2024 University of Stuttgart
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
from time import time
from typing import List, Optional, Sequence, Union, Dict, Tuple
from urllib.parse import urljoin

import requests
from flask.globals import current_app
from qiskit import qasm2
from requests.exceptions import ConnectionError

from qunicorn_core.celery import CELERY
from qunicorn_core.api.api_models.device_dtos import DeviceDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot, PilotJob, PilotJobResult
from qunicorn_core.db.db import DB
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.job_state import TransientJobStateDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.static.qunicorn_exception import QunicornError

DEFAULT_QUANTUM_CIRCUIT = """OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q[1] -> c[1];
measure q[0] -> c[0];
"""

QMWARE_URL = os.environ.get("QMWARE_URL", "https://dispatcher.dev.qmware-dev.cloud/")

# TODO: read token from request body
QMWARE_API_KEY = os.environ.get("QMWARE_API_KEY", "")
QMWARE_API_KEY_ID = os.environ.get("QMWARE_API_KEY_ID", "")

AUTHORIZATION_HEADERS = {
    "X-API-KEY": QMWARE_API_KEY,
    "X-API-KEY-ID": QMWARE_API_KEY_ID,
}


class QMWAREResultsPending(Exception):
    pass


class QMwarePilot(Pilot):
    """Base class for Pilots"""

    provider_name = ProviderName.QMWARE
    supported_languages = tuple([AssemblerLanguage.QASM2])

    def run(self, jobs: Sequence[PilotJob], token: Optional[str] = None):
        """Run a job of type RUNNER on a backend using a Pilot"""
        job_name = "Qunicorn request"

        jobs_to_watch = {}

        for job in jobs:
            job_name = f"{job_name}_{job.job.id}_{job.program.id}"
            if job.circuit_fragment_id:
                job_name = f"{job_name}-{job.circuit_fragment_id}"

            if job.job.executed_on.name == "dev":
                code_type = "qasm2"
            elif job.job.executed_on.name == "dev-gpu":
                code_type = "qasm2-gpu"
            else:
                raise QunicornError(f"Unknown QMware device {job.job.executed_on.name}")

            data = {
                "name": job_name,
                "maxExecutionTimeInMs": 60_000,
                "ttlAfterFinishedInMs": 1_200_000,
                "code": {"type": code_type, "code": job.circuit},
                "selectionParameters": [],
                "programParameters": [{"name": "shots", "value": str(job.job.shots)}],
            }

            response = requests.post(
                urljoin(QMWARE_URL, "/v0/requests"), json=data, headers=AUTHORIZATION_HEADERS, timeout=10
            )
            response.raise_for_status()

            result = response.json()

            if not result["jobCreated"]:
                # TODO save job/program specific error in DB
                raise QunicornError(f"Job was not created. ({result['message']})")

            program_state = TransientJobStateDataclass(
                job=job.job,
                program=job.program,
                circuit_fragment_id=job.circuit_fragment_id,
                data={
                    "type": "QMWARE",
                    "id": result["id"],
                    "started_at": int(time()),
                    "X-API-KEY": QMWARE_API_KEY,
                    "X-API-KEY-ID": QMWARE_API_KEY_ID,
                    "circuit": job.circuit,
                },
            )
            program_state.save()

            jobs_to_watch[job.job.id] = job.job

            if job.job.state not in (JobState.FINISHED, JobState.ERROR, JobState.CANCELED, JobState.BLOCKED):
                job.job.state = JobState.RUNNING.value
                job.job.save()
        DB.session.commit()

        for qunicorn_job in jobs_to_watch.values():
            watch_task = watch_qmware_results.s(job_id=qunicorn_job.id).delay()
            qunicorn_job.celery_id = watch_task.id
            qunicorn_job.save(commit=True)  # commit new celery id

    def _get_job_results(self, qunicorn_job_id: int) -> None:  # noqa: C901
        qunicorn_job: JobDataclass = JobDataclass.get_by_id(qunicorn_job_id)

        if qunicorn_job is None:
            raise ValueError("Unknown Qunicorn job id {qunicorn_job_id}!")

        jobs_to_save = []
        results_to_save = []

        for program_state in tuple(qunicorn_job._transient):
            if program_state.program is None:
                continue  # only process program related transient state

            if not isinstance(program_state.data, dict) or program_state.data.get("type", None) != "QMWARE":
                continue  # only process transient state created by this pilot

            job_started_at = program_state.data["started_at"]
            qmware_job_id = program_state.data["id"]
            program = program_state.program

            if job_started_at + (24 * 3600) < time():
                # time out jobs after 24 hours!
                program_state.delete()
                error = QunicornError(f"QMware job with id {qmware_job_id} timed out!")
                qunicorn_job.save_error(error, program=program)
                continue

            response = requests.get(
                urljoin(QMWARE_URL, f"/v0/jobs/{qmware_job_id}"),
                headers={
                    "X-API-KEY": program_state.data["X-API-KEY"],
                    "X-API-KEY-ID": program_state.data["X-API-KEY-ID"],
                },
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()

            if result["status"] in ("WAITING", "PREPARING", "RUNNING"):
                raise QMWAREResultsPending()

            if result["status"] in ("ERROR", "TIMEOUT", "CANCELED"):
                program_state.delete()
                error = QunicornError(f"QMware job with id {qmware_job_id} returned status {result['status']}")
                qunicorn_job.save_error(error, program=program, extra_data={"qmware_result": result})
                continue

            if result["status"] != "SUCCESS":
                program_state.delete()
                error = QunicornError(f"QMware job with id {qmware_job_id} returned unknown status {result['status']}")
                qunicorn_job.save_error(error, program=program, extra_data={"qmware_result": result})
                continue

            try:
                try:
                    circuit = qasm2.loads(program_state.data["circuit"])
                except qasm2.exceptions.QASM2ParseError:
                    circuit = qasm2.loads(
                        program_state.data["circuit"], custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS
                    )

                register_metadata = []

                for classical_register in circuit.cregs:
                    register_metadata.append(
                        {
                            "name": classical_register.name,
                            "size": classical_register.size,
                        }
                    )

                measurements: List[Dict] = json.loads(result["out"]["value"])
                results: List[List[Dict[str, int]]] = [measurement["result"] for measurement in measurements]

                hex_counts, hex_probabilities = self._convert_qmware_measurements_to_qunicorn_measurements(
                    qunicorn_job, results, register_metadata
                )
            except Exception as err:
                program_state.delete()
                qunicorn_job.save_error(err, program=program, extra_data={"qmware_result": result})
                continue

            jobs_to_save.append(
                PilotJob(
                    circuit=program_state.data["circuit"],
                    job=program_state.job,
                    program=program_state.program,
                    circuit_fragment_id=program_state.circuit_fragment_id,
                )
            )

            results_to_save.append(
                [
                    PilotJobResult(
                        data=hex_counts,
                        result_type=ResultType.COUNTS,
                        meta={
                            "format": "hex",
                            "shots": qunicorn_job.shots,
                            "registers": register_metadata,
                        },
                    ),
                    PilotJobResult(
                        data=hex_probabilities,
                        result_type=ResultType.PROBABILITIES,
                        meta={
                            "format": "hex",
                            "shots": qunicorn_job.shots,
                            "registers": register_metadata,
                        },
                    ),
                ]
            )
            program_state.delete()

        DB.session.commit()

        # this saves the results after all transient states with type QMWARE are deleted so that determine_db_job_state
        # can determine the correct state
        for job, result in zip(jobs_to_save, results_to_save):
            self.save_results(job, result)

        DB.session.commit()

    def _convert_qmware_measurements_to_qunicorn_measurements(
        self, job: JobDataclass, results: List[List[dict[str, int]]], register_metadata: list[dict[str, any]]
    ) -> Tuple[dict[str, int], dict[str, float]]:
        hex_counts = {}
        hex_probabilities = {}

        for single_result in zip(*results):
            hex_measurements = []
            hits = None
            register: Dict[str, int]

            if job.executed_on.name == "dev":
                for register in single_result:
                    hex_measurements.append(hex(register["number"]))

                    if hits is None:
                        hits = register["hits"]
                    else:
                        assert hits == register["hits"], "results have different number of hits"
            elif job.executed_on.name == "dev-gpu":
                # measurements are combined into one register on this device, therefore we have to split them again
                register = single_result[0]
                measured_bits = register["number"]

                for single_register_meta in register_metadata:
                    size: int = single_register_meta["size"]
                    mask = (0b1 << size) - 1

                    hex_measurements.append(hex(measured_bits & mask))

                    # discard already processed bits
                    measured_bits >>= size

                if hits is None:
                    hits = register["hits"]
                else:
                    assert hits == register["hits"], "results have different number of hits"

            if hits is None:
                hits = 0

            hex_measurement = " ".join(hex_measurements)
            hex_counts[hex_measurement] = hits
            hex_probabilities[hex_measurement] = hits / job.shots

        return hex_counts, hex_probabilities

    def determine_db_job_state(self, db_job: JobDataclass) -> JobState:
        if db_job.state == JobState.RUNNING.value:
            if any(t.data.get("type") == "QMWARE" for t in db_job._transient if isinstance(t.data, dict)):
                return JobState.RUNNING
            return JobState.FINISHED
        return super().determine_db_job_state(db_job)

    def execute_provider_specific(self, jobs: Sequence[PilotJob], job_type: str, token: Optional[str] = None):
        """Execute a job of a provider specific type on a backend using a Pilot"""
        raise QunicornError("No valid Job Type specified. QMware Pilot does not support provider specific job types.")

    def get_standard_provider(self) -> ProviderDataclass:
        """Create the standard ProviderDataclass Object for the pilot and return it"""
        found_provider = ProviderDataclass.get_by_name(self.provider_name)

        if not found_provider:
            found_provider = ProviderDataclass(with_token=True, name=self.provider_name)
            found_provider.supported_languages = list(self.supported_languages)
            found_provider.save()  # make sure that the provider will be committed to DB

        return found_provider

    def get_standard_job_with_deployment(self, device: DeviceDataclass) -> JobDataclass:
        """Create the standard ProviderDataclass Object for the pilot and return it"""
        return self.create_default_job_with_circuit_and_device(device, DEFAULT_QUANTUM_CIRCUIT)

    def save_devices_from_provider(self, token: Optional[str]):
        """Access the devices from the cloud service of the provider, to update the current device list of qunicorn"""
        raise QunicornError(
            "The QMware pilot cannot fetch devices because the QMware API doesn't have the concept of devices."
        )

    def is_device_available(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> bool:
        """Check if a device is available for a user"""
        response = requests.get(urljoin(QMWARE_URL, "/health"))

        if response.status_code != 200:
            return False

        content = response.json()

        return content["status"] == "UP"

    def get_device_data_from_provider(self, device: Union[DeviceDataclass, DeviceDto], token: Optional[str]) -> dict:
        """Get device data for a specific device from the provider"""
        raise QunicornError(
            "The QMware pilot cannot fetch devices because the QMware API doesn't have the concept of devices."
        )

    def cancel_provider_specific(self, job: JobDataclass, token: Optional[str] = None):
        """Cancel execution of a job at the corresponding backend"""
        current_app.logger.warning(
            f"Cancel job with id {job.id} on {job.executed_on.provider.name} failed."
            f"Canceling while in execution not supported for QMware Jobs"
        )
        raise QunicornError("Canceling not supported on QMware devices")


@CELERY.task(
    ignore_result=True,
    autoretry_for=(QMWAREResultsPending, ConnectionError),
    retry_backoff=1.2,
    retry_backoff_max=60,
    max_retries=None,
)
def watch_qmware_results(job_id: int):
    QMwarePilot()._get_job_results(job_id)
