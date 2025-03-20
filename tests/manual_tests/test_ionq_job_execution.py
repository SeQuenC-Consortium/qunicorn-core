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

""" "Test class to test the functionality of the job_api"""
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils


def test_create_and_run_runner_with_qiskit():
    test_utils.execute_job_test(ProviderName.IONQ, "ionq_simulator", [AssemblerLanguage.QISKIT])


def test_create_and_run_runner_with_qasm2():
    test_utils.execute_job_test(ProviderName.IONQ, "ionq_simulator", [AssemblerLanguage.QASM2])


def test_create_and_run_runner_with_qasm3():
    test_utils.execute_job_test(ProviderName.IONQ, "ionq_simulator", [AssemblerLanguage.QASM3])


def test_create_and_run_runner_with_braket():
    test_utils.execute_job_test(ProviderName.IONQ, "ionq_simulator", [AssemblerLanguage.BRAKET])


def test_create_and_run_runner_with_qrisp():
    test_utils.execute_job_test(ProviderName.IONQ, "ionq_simulator", [AssemblerLanguage.QRISP])
