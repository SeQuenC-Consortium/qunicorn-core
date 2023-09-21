import datetime
import logging
from typing import Callable

from qunicorn_core.api.api_models import JobCoreDto, DeploymentDto, QuantumProgramDto, UserDto, DeviceDto, ProviderDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.core.pilotmanager.ibm_pilot import IBMPilot
from qunicorn_core.core.transpiler.transpiler_manager import transpile_manager
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_type import JobType
from qunicorn_core.static.enums.programming_language import ProgrammingLanguage
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.static.enums.result_type import ResultType

REQUIRE_PYTHON_EXECUTION = [AssemblerLanguage.QRISP, AssemblerLanguage.BRAKET, AssemblerLanguage.QISKIT]


def execute_in_environment(
    job_dto: JobCoreDto, pilot: Pilot, backend: Pilot, immediate_result_listener: Callable[[list[ResultDataclass]], None]
):
    program = job_dto.deployment.programs[0]
    transpiler = transpile_manager.get_transpiler(program.assembler_language, pilot.supported_language)

    if program.assembler_language not in REQUIRE_PYTHON_EXECUTION:
        if job_dto.type == JobType.RUNNER:
            logging.info(
                f"Running circuit for job {job_dto.id} on {pilot.provider_name} - {pilot.device_name}"
                f" with {job_dto.shots} shots"
            )
            return pilot.run(transpiler(program.quantum_circuit), shots=job_dto.shots)
        elif job_dto.type == JobType.ESTIMATOR:
            logging.info(f"Estimating circuit for job {job_dto.id} on {pilot.provider_name} - {pilot.device_name}")
            return pilot.estimate(transpiler(program.quantum_circuit))
        elif job_dto.type == JobType.SAMPLER:
            logging.info(f"Sampling circuit for job {job_dto.id} on {pilot.provider_name} - {pilot.device_name}")
            return pilot.sample(transpiler(program.quantum_circuit))
        else:
            return pilot.execute(job_dto)

    execution_globals = dict()

    exec(program.quantum_circuit, execution_globals)

    print(execution_globals)

    main_function = execution_globals.get("main")
    if not main_function:
        raise ValueError("no main function found")

    logging.info(f"Starting execution environment for job {job_dto.id}")

    result = main_function(backend=backend)
    return [
        ResultDataclass(result_type=ResultType.COUNTS, result_dict=result if isinstance(result, dict) else None)
    ]


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    job_core = JobCoreDto(
        type=JobType.RUNNER,
        id=22,
        token="62fe069c518b693d31652ac07e1ca4fa6edbc7e866141eef6abf2819e021f88de1b79498d1449620d1a300df1579b3bb92d443e1ac36ef73c408a09b2372e6d5",
        executed_by=None,
        executed_on=DeviceDto(
            id="1",
            name="ibmq_qasm_simulator",
            num_qubits=4,
            provider=ProviderDto(id=33, name=ProviderName.IBM, supported_language=ProgrammingLanguage.QISKIT, with_token=False),
            is_simulator=True,
        ),
        results=None,
        data=None,
        parameters=None,
        state=None,
        shots=200,
        started_at=None,
        finished_at=None,
        progress=None,
        name="test",
        deployment=DeploymentDto(
            deployed_at=datetime.datetime.now(),
            deployed_by=UserDto(name="user", id=44),
            name="test",
            id=1,
            programs=[
                QuantumProgramDto(
                    quantum_circuit="""
import qrisp                        
from qrisp import QuantumCircuit
def main(backend):
    qc_0 = QuantumCircuit(2, 2, name = "fan out")
    qc_0.h(0)
    qc_0.cx(0, range(1,2))
    qc_0.measure(range(0,2), range(0,2))
    backend.run(qc_0)
    backend.estimate(qc_0)
    return {"success": True}
    """,
                    assembler_language=AssemblerLanguage.QRISP,
                )
            ],
        ),
    )

    results = execute_in_environment(job_core, IBMPilot, Pilot, print)

    print(results)


if __name__ == "__main__":
    main()
