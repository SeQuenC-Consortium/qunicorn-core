from datetime import datetime

from pyquil.api import get_qc

from qunicorn_core.api.api_models import JobCoreDto, DeviceDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import job_db_service
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

DEFAULT_QUANTUM_CIRCUIT_2 = """from pyquil import Program \n
from pyquil.gates import * \n
from pyquil.quilbase import Declare\n
circuit = Program(
Declare(\"ro\", \"BIT\", 2),
H(0),
H(0),
CNOT(0, 1),
MEASURE(0, (\"ro\", 0)),
MEASURE(1, (\"ro\", 1)),
)"""

DEFAULT_QUANTUM_CIRCUIT_1 = """from pyquil import Program \n
from pyquil.gates import * \n
from pyquil.quilbase import Declare\n
circuit = Program(
Declare(\"ro\", \"BIT\", 2),
H(0),
CNOT(0, 1),
MEASURE(0, (\"ro\", 0)),
MEASURE(1, (\"ro\", 1)),
)"""


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
                qvm = get_qc(job_core_dto.executed_on.name)
                qvm_result = qvm.run(qvm.compile(program)).get_register_map().get("ro")
                result_dict = RigettiPilot.result_to_dict(qvm_result)
                result_dict = RigettiPilot.qubit_binary_to_hex(result_dict, job_core_dto.id)
                probabilities_dict = RigettiPilot.calculate_probabilities(result_dict)
                result = ResultDataclass(
                    circuit=job_core_dto.deployment.programs[program_index].quantum_circuit,
                    result_dict={"counts": result_dict, "probabilities": probabilities_dict},
                    result_type=ResultType.COUNTS,
                    meta_data="",
                )
                program_index += 1
                results.append(result)
            return results
        else:
            raise job_db_service.return_exception_and_update_job(
                job_core_dto.id, ValueError("Device need to be local for RIGETTI")
            )

    @staticmethod
    def result_to_dict(results: []) -> dict:
        """Converts the result of the qvm to a dictionary"""
        results_as_strings = []
        for row in results:
            row_as_string = ""
            for index in range(0, len(row)):
                row_as_string += str(row[index])
            results_as_strings.append(row_as_string)
        result_set = set(results_as_strings)
        result_dict = {}
        for result_element in result_set:
            result_dict.update({result_element: results_as_strings.count(result_element)})
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
                quantum_circuit=DEFAULT_QUANTUM_CIRCUIT_1,
                assembler_language=language,
            ),
            QuantumProgramDataclass(
                quantum_circuit=DEFAULT_QUANTUM_CIRCUIT_2,
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
            results=[
                ResultDataclass(
                    result_dict={
                        "counts": {"0x0": 2007, "0x3": 1993},
                        "probabilities": {"0x0": 0.50175, "0x3": 0.49825},
                    }
                )
            ],
        )

    def save_devices_from_provider(self, device_request):
        raise ValueError("Rigetti Pilot cannot fetch Devices from Rigetti Computing, because there is no Cloud Access.")

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
