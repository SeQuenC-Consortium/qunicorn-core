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

from qunicorn_core.api.api_models.job_dtos import (
    JobCoreDto,
)
from qunicorn_core.celery import CELERY
from qunicorn_core.core.mapper import result_mapper
from qunicorn_core.core.pilotmanager.pilot_manager import PILOTS
from qunicorn_core.core.transpiler.preprocessing_manager import preprocessing_manager
from qunicorn_core.core.transpiler.transpiler_manager import transpile_manager
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider_assembler_language import ProviderAssemblerLanguageDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.qunicorn_exception import QunicornError
from qunicorn_core.util import logging

"""This Class is responsible for running a job on a pilot and scheduling them with celery"""

ASYNCHRONOUS: bool = environ.get("EXECUTE_CELERY_TASK_ASYNCHRONOUS") == "True"


@CELERY.task()
def run_job(job_core_dto_dict: dict):
    """Assign the job to the target pilot which executes the job"""
    job_core_dto: JobCoreDto = yaml.load(job_core_dto_dict["data"], yaml.Loader)
    job_db_service.update_attribute(job_core_dto.id, JobState.RUNNING, JobDataclass.state)
    device = job_core_dto.executed_on
    results: Optional[list[ResultDataclass]] = None

    for pilot in PILOTS:
        if pilot.has_same_provider(device.provider.name):
            __transpile_circuits(job_core_dto, pilot.supported_languages)
            logging.info(f"Run job with id {job_core_dto.id} on {pilot.__class__}")
            results = pilot.execute(job_core_dto)
            break

    if results is None:
        exception: Exception = QunicornError("No valid Target specified")
        job_db_service.update_finished_job(
            job_core_dto.id, result_mapper.exception_to_error_results(exception), JobState.ERROR
        )
        raise exception

    job_db_service.update_finished_job(job_core_dto.id, results)
    logging.info(f"Run job with id {job_core_dto.id} and get the result {results}")


def __transpile_circuits(job_dto: JobCoreDto, dest_languages: [ProviderAssemblerLanguageDataclass]):
    """Transforms all circuits of the deployment into the circuits in the destination language"""
    logging.info(f"Transpile all circuits of job with id{job_dto.id}")
    error_results: list[ResultDataclass] = []
    job_dto.transpiled_circuits = []

    # Transform each circuit into a transpiled circuit for the necessary language
    for program in job_dto.deployment.programs:
        src_language: AssemblerLanguage = program.assembler_language
        try:
            # Preprocess a string to a circuit object if necessary
            preprocessor = preprocessing_manager.get_preprocessor(src_language)
            circuit = preprocessor(program.quantum_circuit)

            # We only need to transpile, when the source language is not the destination language
            if src_language in dest_languages:
                job_dto.transpiled_circuits.append(circuit)
                continue

            # Transpile the circuit to the destination language
            transpiler = transpile_manager.get_transpiler(src_language, dest_languages)
            job_dto.transpiled_circuits.append(transpiler(circuit))
        except Exception as exception:
            error_results.extend(result_mapper.exception_to_error_results(exception, program.quantum_circuit))

    # If an error was caught -> Update the job and raise it again
    if len(error_results) > 0:
        job_db_service.update_finished_job(job_dto.id, error_results, JobState.ERROR)
        string_errors = " ".join(str(error.result_dict.get("exception_message", "")) for error in error_results)
        if string_errors:
            raise QunicornError("Transpilation Error: " + string_errors)


def cancel_job(job_core_dto):
    """cancel job execution"""
    device = job_core_dto.executed_on
    for pilot in PILOTS:
        if pilot.has_same_provider(device.provider.name):
            pilot.cancel(job_core_dto)
            return
