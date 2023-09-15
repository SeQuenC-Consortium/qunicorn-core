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
from datetime import datetime

from braket.devices import LocalSimulator
from braket.tasks import GateModelQuantumTaskResult
from braket.tasks.local_quantum_task_batch import LocalQuantumTaskBatch

from qunicorn_core.api.api_models import DeviceDto
from qunicorn_core.api.api_models.job_dtos import JobCoreDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import device_db_service, provider_db_service
from qunicorn_core.db.database_services.job_db_service import return_exception_and_update_job
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.pilot_assembler_language_list import PilotAssemblerLanguageListDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.db.models.user import UserDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.util import logging


class AWSPilot(Pilot):
    """The AWS Pilot"""

    provider_name: ProviderName = ProviderName.AWS

    supported_languages: [PilotAssemblerLanguageListDataclass] = [
        PilotAssemblerLanguageListDataclass(provider_ID=2, programming_language=AssemblerLanguage.BRAKET),
        PilotAssemblerLanguageListDataclass(provider_ID=2, programming_language=AssemblerLanguage.QASM3),
    ]

    def run(self, job_core_dto: JobCoreDto):
        """Execute the job on a local simulator and saves results in the database"""
        if not job_core_dto.executed_on.is_local:
            raise return_exception_and_update_job(job_core_dto.id, ValueError("Device need to be local for AWS"))

        device = LocalSimulator()
        quantum_tasks: LocalQuantumTaskBatch = device.run_batch(
            job_core_dto.transpiled_circuits, shots=job_core_dto.shots
        )
        aws_simulator_results: list[GateModelQuantumTaskResult] = quantum_tasks.results()
        return AWSPilot.__map_simulator_results_to_dataclass(aws_simulator_results, job_core_dto)

    def execute_provider_specific(self, job_core_dto: JobCoreDto):
        """Execute a job of a provider specific type on a backend using a Pilot"""

        raise return_exception_and_update_job(job_core_dto.id, ValueError("No valid Job Type specified"))

    @staticmethod
    def __map_simulator_results_to_dataclass(
        aws_results: list[GateModelQuantumTaskResult], job_dto: JobCoreDto
    ) -> list[ResultDataclass]:
        """Map the results from the aws simulator to a result dataclass object"""
        result_dtos: list[ResultDataclass] = [
            ResultDataclass(
                result_dict={
                    "counts": dict(aws_result.measurement_counts.items()),
                    "probabilities": aws_result.measurement_probabilities,
                },
                job_id=job_dto.id,
                circuit=aws_result.additional_metadata.action.source,
                meta_data="",
                result_type=ResultType.COUNTS,
            )
            for aws_result in aws_results
        ]
        return result_dtos

    def get_standard_job_with_deployment(self, user: UserDataclass, device: DeviceDataclass) -> JobDataclass:
        """Get the standard job including its deployment for a certain user and device"""
        language: AssemblerLanguage = AssemblerLanguage.QASM3
        qasm3_str: str = (
            "OPENQASM 3; \nqubit[3] q;\nbit[3] c;\nh q[0];\ncnot q[0], q[1];\ncnot q[1], q[2];\nc = " "measure q;"
        )
        programs: list[QuantumProgramDataclass] = [
            QuantumProgramDataclass(quantum_circuit=qasm3_str, assembler_language=language)
        ]
        deployment = DeploymentDataclass(
            deployed_by=user, programs=programs, deployed_at=datetime.now(), name="DeploymentAWSQasmName"
        )

        return JobDataclass(
            executed_by=user,
            executed_on=device,
            deployment=deployment,
            progress=0,
            state=JobState.READY,
            shots=4000,
            type=JobType.RUNNER,
            started_at=datetime.now(),
            name="AWSJob",
            results=[
                ResultDataclass(
                    result_dict={
                        "counts": {"000": 2007, "111": 1993},
                        "probabilities": {"000": 0.50175, "111": 0.49825},
                    }
                )
            ],
        )

    def save_devices_from_provider(self, device_request):
        """
        Save the available aws device into the database.
        Since there is currently only a local simulator in use, the device_request parameter is unused.
        """
        provider: ProviderDataclass = provider_db_service.get_provider_by_name(self.provider_name)
        aws_device: DeviceDataclass = DeviceDataclass(
            provider_id=provider.id,
            num_qubits=-1,
            name="local_simulator",
            is_simulator=True,
            is_local=True,
            provider=provider,
        )
        device_db_service.save_device_by_name(aws_device)

    def get_standard_provider(self):
        return ProviderDataclass(
            with_token=False, supported_languages=self.supported_languages, name=self.provider_name
        )

    def is_device_available(self, device: DeviceDto, token: str) -> bool:
        logging.info("AWS local simulator is always available")
        return True
