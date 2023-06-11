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


from qunicorn_core.celery import CELERY
from .pilot_base import Pilot
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_provider import IBMProvider


class QiskitPilot(Pilot):
    """The Qiskit Pilot"""

    IMBQ_BACKEND = "ibmq_qasm_simulator"

    def execute(self, job):
        """Execute a job on an IBM backend using the Qiskit Pilot"""

        provider = self.__get_ibm_provider(job.token)
        backend, transpiled = self.transpile(provider, job.circuit)

        job_from_ibm = backend.run(transpiled, shots=job.shots)
        counts = job_from_ibm.result().get_counts()

        print(f"Executing job {job_from_ibm} on {job.provider} with the Qiskit Pilot and get the result {counts}")
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
        backend = provider.get_backend(self.IMBQ_BACKEND)
        transpiled = transpile(qasm_circ, backend=backend)

        print(f"Transpile a quantum circuit for a specific IBM backend")
        return backend, transpiled


class AWSPilot(Pilot):
    """The AWS Pilot"""

    def execute(self, job):
        print(f"Executing job {job} with AWS Pilot")

    def transpile(self, job):
        """Transpile job on an IBM backend, needs a device_id"""    

        print(f"Transpile a quantum circuit for a specific AWS backend")





