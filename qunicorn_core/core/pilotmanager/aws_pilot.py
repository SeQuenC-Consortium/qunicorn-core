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

from braket.devices import LocalSimulator
from braket.ir.openqasm import Program
from braket.tasks import GateModelQuantumTaskResult
from braket.tasks.local_quantum_task_batch import LocalQuantumTaskBatch

from qunicorn_core.api.api_models import DeviceDto
from qunicorn_core.api.api_models.job_dtos import JobCoreDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.provider_assembler_language import ProviderAssemblerLanguageDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.static.qunicorn_exception import QunicornError
from qunicorn_core.util import logging


class AWSPilot(Pilot):
    """The AWS Pilot"""

    provider_name: ProviderName = ProviderName.AWS
    supported_languages: list[AssemblerLanguage] = [AssemblerLanguage.BRAKET, AssemblerLanguage.QASM3]

    def run(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute the job on a local simulator and saves results in the database"""
        if not job_core_dto.executed_on.is_local:
            raise job_db_service.return_exception_and_update_job(
                job_core_dto.id, QunicornError("Device not found, device needs to be local for AWS")
            )

        # Since QASM is stored as a string, it needs to be converted to a QASM program before execution
        for index in range(len(job_core_dto.transpiled_circuits)):
            if type(job_core_dto.transpiled_circuits[index]) is str:
                job_core_dto.transpiled_circuits[index] = Program(source=job_core_dto.transpiled_circuits[index])

        quantum_tasks: LocalQuantumTaskBatch = LocalSimulator().run_batch(
            job_core_dto.transpiled_circuits, shots=job_core_dto.shots
        )

        return AWSPilot.__map_aws_results_to_dataclass(quantum_tasks.results(), job_core_dto)

    def execute_provider_specific(self, job_core_dto: JobCoreDto):
        """Execute a job of a provider specific type on a backend using a pilot"""
        raise job_db_service.return_exception_and_update_job(
            job_core_dto.id, QunicornError("No valid Job Type specified")
        )

    def cancel_provider_specific(self, job_dto):
        logging.warn(
            f"Cancel job with id {job_dto.id} on {job_dto.executed_on.provider.name} failed."
            f"Canceling while in execution not supported for AWS Jobs"
        )
        raise QunicornError("Canceling not supported on AWS devices")

    @staticmethod
    def __map_aws_results_to_dataclass(
        aws_results: list[GateModelQuantumTaskResult], job_dto: JobCoreDto
    ) -> list[ResultDataclass]:
        """Map the results from the aws simulator to a result dataclass object"""
        job_id: int = job_dto.id
        return [
            ResultDataclass(
                result_dict={
                    "counts": Pilot.qubit_binary_to_hex(aws_results[i].measurement_counts, job_id),
                    "probabilities": Pilot.qubit_binary_to_hex(aws_results[i].measurement_probabilities, job_id),
                },
                job_id=job_id,
                circuit=job_dto.deployment.programs[i].quantum_circuit,
                meta_data="",
                result_type=ResultType.COUNTS,
            )
            for i in range(len(aws_results))
        ]

    def get_standard_job_with_deployment(self, device: DeviceDataclass) -> JobDataclass:
        return self.create_default_job_with_circuit_and_device(device, "qunicorn-circuit")

    def save_devices_from_provider(self, device_request):
        raise QunicornError("AWS Pilot cannot fetch Devices from AWS API, because there is no Cloud Access.")

    def get_standard_provider(self) -> ProviderDataclass:
        return ProviderDataclass(
            with_token=False,
            supported_languages=[
                ProviderAssemblerLanguageDataclass(supported_language=language) for language in self.supported_languages
            ],
            name=self.provider_name,
        )

    def is_device_available(self, device: DeviceDto, token: str) -> bool:
        logging.info("AWS local simulator is always available")
        return True
