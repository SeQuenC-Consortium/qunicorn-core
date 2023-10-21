from datetime import datetime

import numpy
from pyquil.api import get_qc

from qunicorn_core.api.api_models import JobCoreDto, DeviceDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import provider_db_service, device_db_service, job_db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass
from qunicorn_core.db.models.provider_assembler_language import ProviderAssemblerLanguageDataclass
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_state import JobState
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType
from qunicorn_core.util import logging


class RigettiPilot(Pilot):
    """The Rigetti Pilot"""

    provider_name: ProviderName = ProviderName.RIGETTI

    supported_languages: list[AssemblerLanguage] = [AssemblerLanguage.QUIL]

    def run(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute the job on a local simulator and saves results in the database"""
        if job_core_dto.executed_on.is_local:
            results = []
            program_index = 0
            for program in job_core_dto.transpiled_circuits:
                program.wrap_in_numshots_loop(job_core_dto.shots)
                qvm = get_qc("9q-square-qvm")
                qvm_result = qvm.run(qvm.compile(program)).readout_data.get("ro")
                result_dict = RigettiPilot.result_to_dict(qvm_result)
                result = ResultDataclass(
                    circuit=job_core_dto.deployment.programs[program_index].quantum_circuit,
                    result_dict={"counts": result_dict, "probabilities": {}},
                    result_type=ResultType.COUNTS,
                    meta_data="",
                )

                results.append(result)
            return results
        else:
            raise job_db_service.return_exception_and_update_job(
                job_core_dto.id, ValueError("Device need to be local for RIGETTI")
            )

    @staticmethod
    def result_to_dict(string_result):
        qubit0result = sum(numpy.array(string_result)[:, 0])
        qubit1result = sum(numpy.array(string_result)[:, 1])
        result_dict = {"0x0": float(qubit0result), "0x3": float(qubit1result)}
        return result_dict

    def execute_provider_specific(self, job_core_dto: JobCoreDto):
        """Execute a job of a provider specific type on a backend using a Pilot"""

        raise job_db_service.return_exception_and_update_job(job_core_dto.id, ValueError("No valid Job Type specified"))

    def cancel_provider_specific(self, job_dto):
        raise ValueError("Canceling not implemented for rigetti pilot yet")

    def get_standard_job_with_deployment(self, device: DeviceDataclass) -> JobDataclass:
        language: AssemblerLanguage = AssemblerLanguage.QUIL
        programs: list[QuantumProgramDataclass] = [
            QuantumProgramDataclass(
                quantum_circuit="""from pyquil import Program \n
from pyquil.gates import * \n
from pyquil.quilbase import Declare\n
program = Program(
Declare(\"ro\", \"BIT\", 2),
H(0),
CNOT(0, 1),
MEASURE(0, (\"ro\", 0)),
MEASURE(1, (\"ro\", 1)),
).wrap_in_numshots_loop(10)""",
                assembler_language=language,
            ),
            QuantumProgramDataclass(
                quantum_circuit="""from pyquil import Program \n
from pyquil.gates import * \n
from pyquil.quilbase import Declare\n
program = Program(
Declare(\"ro\", \"BIT\", 2),
H(0),
CNOT(0, 1),
MEASURE(0, (\"ro\", 0)),
MEASURE(1, (\"ro\", 1)),
).wrap_in_numshots_loop(10)""",
                assembler_language=language,
            ),
        ]
        deployment = DeploymentDataclass(
            deployed_by=None,
            programs=programs,
            deployed_at=datetime.now(),
            name="DeploymentRigettiQasmName",
        )

        return JobDataclass(
            executed_by=None,
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

    @staticmethod
    def calculate_probabilities(counts: dict) -> dict:
        """Calculates the probabilities from the counts, probability = counts / total_counts"""

        total_counts = sum(counts.values())
        probabilities = {}
        for key, value in counts.items():
            probabilities[key] = value / total_counts
        return probabilities
