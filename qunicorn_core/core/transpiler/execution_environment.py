import datetime

from qunicorn_core.api.api_models import JobCoreDto, DeploymentDto, QuantumProgramDto, UserDto, DeviceDto
from qunicorn_core.core.pilotmanager.aws_pilot import AWSPilot
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.core.pilotmanager.qiskit_pilot import QiskitPilot
from qunicorn_core.core.transpiler.transpiler_manager import transpile_manager
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.job_type import JobType

REQUIRE_PYTHON_EXECUTION = [AssemblerLanguage.QRISP, AssemblerLanguage.BRAKET, AssemblerLanguage.QISKIT]


def execute_in_environment(job_dto: JobCoreDto,
                           pilot: Pilot):
    program = job_dto.deployment.programs[0]
    transpiler = transpile_manager.get_transpiler(program.assembler_language, pilot.LANGUAGE)

    class Backend:

        def run(self, circuit):
            pilot.run(job_dto, transpiler(circuit))

        def estimate(self, circuit):
            pilot.estimate(job_dto, transpiler(circuit))

        def sample(self, circuit):
            pilot.sample(job_dto, transpiler(circuit))

    if program.assembler_language not in REQUIRE_PYTHON_EXECUTION:
        if job_dto.type == JobType.RUNNER:
            return pilot.run(job_dto, transpiler(program.quantum_circuit))
        elif job_dto.type == JobType.ESTIMATOR:
            return pilot.estimate(job_dto, transpiler(program.quantum_circuit))
        elif job_dto.type == JobType.SAMPLER:
            return pilot.sample(job_dto, transpiler(program.quantum_circuit))
        else:
            return pilot.execute(job_dto)

    execution_globals = dict()
    exec(program.quantum_circuit, execution_globals)

    main_function = execution_globals.get("main")
    if not main_function:
        raise ValueError("no main function found")
    backend = Backend()
    main_function(backend=backend)


execute_in_environment(JobCoreDto(type=JobType.RUNNER,
                                  id=22,
                                  executed_by=None,
                                  executed_on=DeviceDto(id="1", device_name="local_simulator", num_qubits=2,
                                                        is_simulator=True),
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
                                      deployed_by=UserDto(
                                          name="user",
                                          id=44
                                      ),
                                      name="test",
                                      id=1,
                                      programs=[QuantumProgramDto(
                                          quantum_circuit="""
import qrisp

from qrisp import QuantumCircuit
def main(backend):
    qc_0 = QuantumCircuit(4, name = "fan out")
    qc_0.h(0)
    qc_0.cx(0, range(1,4))
    backend.run(qc_0)
                                          """,
                                          assembler_language=AssemblerLanguage.QRISP
                                      )]
                                  )), AWSPilot("aws"))
