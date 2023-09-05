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
from os import environ
from typing import Optional

import yaml
from braket.circuits import Circuit
from qiskit import QuantumCircuit

from qunicorn_core.api.api_models import DeviceRequestDto, SimpleDeviceDto
from qunicorn_core.api.api_models.job_dtos import (
    JobCoreDto,
)
from qunicorn_core.celery import CELERY
from qunicorn_core.core.mapper import result_mapper, device_mapper
from qunicorn_core.core.pilotmanager.aws_pilot import AWSPilot
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.core.pilotmanager.ibm_pilot import IBMPilot
from qunicorn_core.core.transpiler.transpiler_manager import transpile_manager
from qunicorn_core.db.database_services import job_db_service, device_db_service, user_db_service, db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.db.models.user import UserDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.util import logging

ASYNCHRONOUS: bool = environ.get("EXECUTE_CELERY_TASK_ASYNCHRONOUS") == "True"

PILOTS: list[Pilot] = [IBMPilot(), AWSPilot()]


@CELERY.task()
def run_job(job_core_dto_dict: dict):
    """Assign the job to the target pilot which executes the job"""

    job_core_dto: JobCoreDto = yaml.load(job_core_dto_dict["data"], yaml.Loader)

    device = job_core_dto.executed_on
    job_db_service.update_attribute(job_core_dto.id, JobState.RUNNING, JobDataclass.state)
    results: Optional[list[ResultDataclass]] = None

    for pilot in PILOTS:
        if pilot.is_my_provider(device.provider.name):
            """
            TODO when multiple languages are supported maybe pick a specific instead of default since for example qasm3
            can be directly used for aws instead of transpiling it manually to braket
            """
            __transpile_circuits(job_core_dto, pilot.supported_language[0])
            pilot.get_standard_devices()
            logging.info(f"Run job with id {job_core_dto.id} on {pilot.__class__}")
            results = pilot.execute(job_core_dto)
            break

    if results is None:
        exception: Exception = ValueError("No valid Target specified")
        job_db_service.update_finished_job(
            job_core_dto.id, result_mapper.exception_to_error_results(exception), JobState.ERROR
        )
        raise exception

    job_db_service.update_finished_job(job_core_dto.id, results)
    logging.info(f"Run job with id {job_core_dto.id} and get the result {results}")


def __transpile_circuits(job_dto: JobCoreDto, destination_language: AssemblerLanguage):
    """Transforms the circuit string into IBM QuantumCircuit objects"""
    logging.info(f"Transpile all circuits of job with id{job_dto.id}")
    error_results: list[ResultDataclass] = []
    job_dto.transpiled_circuits = []

    # Transform each circuit into a transpiled circuit for the necessary language
    for program in job_dto.deployment.programs:
        try:
            if program.assembler_language == AssemblerLanguage.QISKIT:
                quantum_circuit = get_circuit_when_qiskit_on_ibm(program)
            elif program.assembler_language == AssemblerLanguage.BRAKET:
                quantum_circuit = get_circuit_when_braket_on_aws(program)
            else:
                quantum_circuit = program.quantum_circuit

            transpiler = transpile_manager.get_transpiler(
                src_language=program.assembler_language, dest_language=destination_language
            )
            transpiled_circuit = transpiler(quantum_circuit)
            job_dto.transpiled_circuits.append(transpiled_circuit)
        except Exception as exception:
            error_results.extend(result_mapper.exception_to_error_results(exception, program.quantum_circuit))

    # If an error was caught -> Update the job and raise it again
    if len(error_results) > 0:
        job_db_service.update_finished_job(job_dto.id, error_results, JobState.ERROR)
        raise Exception("TranspileError")


def get_circuit_when_qiskit_on_ibm(program):
    """
    since the qiskit circuit modifies the circuit object instead of simple returning the object (it
    returns the instruction set) the 'qiskit_circuit' is modified from the exec
    """
    circuit_globals = {"QuantumCircuit": QuantumCircuit}
    exec(program.quantum_circuit, circuit_globals)
    return circuit_globals["qiskit_circuit"]


def get_circuit_when_braket_on_aws(program):
    """
    Method to remove switching away from braket to qasm and back to braket
    """
    # braket.Circuit needs to be included here as an import here so eval works with the type
    circuit: Circuit = eval(program.quantum_circuit)
    return circuit


def save_default_jobs_and_devices_from_provider():
    user: UserDataclass = user_db_service.get_default_user()
    for pilot in PILOTS:
        device_list_without_default, default_device = pilot.get_standard_devices()
        saved_device = device_db_service.save_device_by_name(default_device)
        job: JobDataclass = pilot.get_standard_job_with_deployment(user, saved_device)
        db_service.get_session().add(job)
        db_service.get_session().add_all(device_list_without_default)
        db_service.get_session().commit()


def save_and_get_devices_from_provider(device_request: DeviceRequestDto) -> list[SimpleDeviceDto]:
    for pilot in PILOTS:
        if pilot.is_my_provider(device_request):
            pilot.save_devices_from_provider(device_request)
    return [device_mapper.dataclass_to_simple(device) for device in device_db_service.get_all_devices()]
