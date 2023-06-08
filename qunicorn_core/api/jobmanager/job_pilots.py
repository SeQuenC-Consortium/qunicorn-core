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

    def get_ibm_provider(self, token:str) -> IBMProvider:
        """Save account credentials and get provider"""
        
        # Save account credentials.
        # You can get you token in your account settings of the front page
        IBMProvider.save_account(token=token, overwrite=True)

        # Load previously saved account credentials.
        return IBMProvider()

    def execute(self, backend, transpiled):
        """Execute a job on an IBM backend using the Qiskit Pilot"""

        job = backend.run(transpiled)
        counts = job.result().get_counts()

        print(f"Executing job {job} with the Qiskit Pilot and get the result {counts}")
        return counts

    def transpile(self, provider: IBMProvider, quantum_circuit_string: str):
        """Transpile job on an IBM backend, needs a device_id"""

        qasm_circ = QuantumCircuit().from_qasm_str(quantum_circuit_string)
        backend = provider.get_backend("ibmq_qasm_simulator")
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





