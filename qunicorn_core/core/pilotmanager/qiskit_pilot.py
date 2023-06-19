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


from qiskit import QuantumCircuit, transpile
from qiskit_ibm_provider import IBMProvider

from qunicorn_core.api.api_models import JobCoreDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.database_services import job_db_service
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.static.enums.job_state import JobState


class QiskitPilot(Pilot):
    """The Qiskit Pilot"""

    IBMQ_BACKEND = "ibmq_qasm_simulator"

    def execute(self, job_dto: JobCoreDto):
        """Execute a job on an IBM backend using the Qiskit Pilot"""

        provider = self.__get_ibm_provider(job_dto.token)
        backend, transpiled = self.transpile(
            provider, job_dto.deployment.quantum_program.quantum_circuit
        )
        job_id = job_dto.id

        job_db_service.update_attribute(job_id, JobState.RUNNING, JobDataclass.state)

        job_from_ibm = backend.run(transpiled, shots=job_dto.shots)
        counts = job_from_ibm.result().get_counts()
        job_db_service.update_result_and_state(job_id, JobState.FINISHED, str(counts))

        print(f"Job with id {job_id} complete")
        print(
            f"Executing job {job_from_ibm} "
            f"on {job_dto.executed_on.provider.name} with the Qiskit Pilot and get the result {counts}"
        )
        return counts

    @staticmethod
    def __get_ibm_provider(token: str) -> IBMProvider:
        """Save account credentials and get provider"""

        # Save account credentials.
        # You can get you token in your account settings of the front page
        IBMProvider.save_account(token=token, overwrite=True)

        # Load previously saved account credentials.
        return IBMProvider()

    def transpile(self, provider: IBMProvider, quantum_circuit_string: str):
        """Transpile job on an IBM backend, needs a device_id"""

        qasm_circ = QuantumCircuit().from_qasm_str(quantum_circuit_string)
        backend = provider.get_backend(self.IBMQ_BACKEND)
        transpiled = transpile(qasm_circ, backend=backend)

        print("Transpile a quantum circuit for a specific IBM backend")
        return backend, transpiled
