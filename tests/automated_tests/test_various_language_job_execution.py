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

"""test in-request execution for aws"""

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils


def test_qasm2_and_qasm3_aws_job_execution():
    test_utils.execute_job_test(ProviderName.AWS, "local_simulator", [AssemblerLanguage.QASM2, AssemblerLanguage.QASM3])


def test_qasm2_and_qasm3_ibm_job_execution():
    test_utils.execute_job_test(ProviderName.IBM, "aer_simulator", [AssemblerLanguage.QASM2, AssemblerLanguage.QASM3])


def test_qasm2_and_qiskit_aws_job_execution():
    test_utils.execute_job_test(ProviderName.AWS, "local_simulator",
                                [AssemblerLanguage.QASM2, AssemblerLanguage.QISKIT])


def test_qasm2_and_qiskit_ibm_job_execution():
    test_utils.execute_job_test(ProviderName.IBM, "aer_simulator", [AssemblerLanguage.QASM2, AssemblerLanguage.QISKIT])


def test_qiskit_and_qasm3_aws_job_execution():
    test_utils.execute_job_test(ProviderName.AWS, "local_simulator",
                                [AssemblerLanguage.QISKIT, AssemblerLanguage.QASM3])


def test_qiskit_and_qasm3_ibm_job_execution():
    test_utils.execute_job_test(ProviderName.IBM, "aer_simulator",
                                [AssemblerLanguage.QISKIT, AssemblerLanguage.QASM3])


def test_qiskit_and_braket_aws_job_execution():
    test_utils.execute_job_test(ProviderName.AWS, "local_simulator",
                                [AssemblerLanguage.QISKIT, AssemblerLanguage.BRAKET])


def test_qiskit_and_braket_ibm_job_execution():
    test_utils.execute_job_test(ProviderName.IBM, "aer_simulator",
                                [AssemblerLanguage.QISKIT, AssemblerLanguage.BRAKET])
