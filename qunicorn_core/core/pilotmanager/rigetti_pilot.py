import os
from datetime import datetime

from pyquil import get_qc
from pyquil.api._qam import QAMExecutionResult

from qunicorn_core.api.api_models import JobCoreDto, DeviceDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.core.pilotmanager.rigetti_utils import get_qpu, get_qvm
from qunicorn_core.db.database_services import provider_db_service, device_db_service
from qunicorn_core.db.database_services.job_db_service import return_exception_and_update_job
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.provider_assembler_language import ProviderAssemblerLanguageDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.db.models.user import UserDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.util import logging


class RigettiPilot(Pilot):
    """The AWS Pilot"""

    provider_name: ProviderName = ProviderName.RIGETTI

    supported_languages: list[AssemblerLanguage] = [AssemblerLanguage.QUIL]

    def run(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute the job on a local simulator and saves results in the database"""
        if False:  # job_core_dto.executed_on.is_local:
            results = []
            for program in job_core_dto.transpiled_circuits:
                qc = get_qc(job_core_dto.deployment.device.name)
                executable = qc.compile(program)
                result: QAMExecutionResult = qc.run(executable)
                string_result = result.data
                results.append(string_result)

            final_results = [ResultDataclass(
                circuit=job_core_dto.deployment.programs[0].quantum_circuit,
                result_dict={"counts": 0, "probabilities": 0},
                result_type=ResultType.COUNTS,
                meta_data=result
            ) for result in results]
            print(final_results)
            return final_results
        else:
            os.environ["AZURE_QUANTUM_SUBSCRIPTION_ID"] = ""
            os.environ["AZURE_QUANTUM_WORKSPACE_RG"] = "AzureQuantum"
            os.environ["AZURE_QUANTUM_WORKSPACE_NAME"] = "qunicorn-enpro"
            os.environ["AZURE_QUANTUM_WORKSPACE_LOCATION"] = "Germany West Central"

            os.environ["AZURE_TENANT_ID"] = ""
            os.environ["AZURE_CLIENT_ID"] = ""
            os.environ["AZURE_CLIENT_SECRET"] = ""

            program = job_core_dto.transpiled_circuits[0]

            qpu = get_qpu("aspen-m-3")
            qvm = get_qvm()

            exe = qpu.compile(program)  # This does not run quilc yet.
            results = qpu.run(exe)  # Quilc will run in the cloud before executing the program.
            qvm_results = qvm.run(exe)
            print(results)
            print(qvm_results)

    def execute_provider_specific(self, job_core_dto: JobCoreDto):
        """Execute a job of a provider specific type on a backend using a Pilot"""

        raise return_exception_and_update_job(job_core_dto.id, ValueError("No valid Job Type specified"))

    def cancel_provider_specific(self, job_dto):
        raise ValueError("Canceling not implemented for rigetti pilot yet")

    def get_standard_job_with_deployment(self, user: UserDataclass, device: DeviceDataclass) -> JobDataclass:
        language: AssemblerLanguage = AssemblerLanguage.QUIL
        programs: list[QuantumProgramDataclass] = [
            QuantumProgramDataclass(quantum_circuit='''from pyquil import Program \n
from pyquil.gates import * \n
from pyquil.quilbase import Declare\n
program = Program(
Declare(\"ro\", \"BIT\", 2),
H(0),
CNOT(0, 1),
MEASURE(0, (\"ro\", 0)),
MEASURE(1, (\"ro\", 1)),
).wrap_in_numshots_loop(10)''', assembler_language=language),
            QuantumProgramDataclass(
                quantum_circuit='''from pyquil import Program \n
from pyquil.gates import * \n
from pyquil.quilbase import Declare\n
program = Program(
Declare(\"ro\", \"BIT\", 2),
H(0),
CNOT(0, 1),
MEASURE(0, (\"ro\", 0)),
MEASURE(1, (\"ro\", 1)),
).wrap_in_numshots_loop(10)''', assembler_language=language),
        ]
        deployment = DeploymentDataclass(
            deployed_by=user,
            programs=programs,
            deployed_at=datetime.now(),
            name="DeploymentRigettiQasmName",
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
            name="RigettiJob",
            results=[ResultDataclass(result_dict={"0x": "550", "1x": "450"})],
        )

    def save_devices_from_provider(self, device_request):
        """
        Save the available aws device into the database.
        Since there is currently only a local simulator in use, the device_request parameter is unused.
        """
        provider: ProviderDataclass = provider_db_service.get_provider_by_name(self.provider_name)
        rigetti_device: DeviceDataclass = DeviceDataclass(
            provider_id=provider.id,
            num_qubits=-1,
            name="9q-qvm",
            is_simulator=True,
            is_local=False,
            provider=provider,
        )
        device_db_service.save_device_by_name(rigetti_device)

    def get_standard_provider(self):
        return ProviderDataclass(
            with_token=False,
            supported_languages=[
                ProviderAssemblerLanguageDataclass(supported_language=language) for language in self.supported_languages
            ],
            name=self.provider_name,
        )

    def is_device_available(self, device: DeviceDto, token: str) -> bool:
        logging.info("Rigetti local simulator is always available")
        return True
