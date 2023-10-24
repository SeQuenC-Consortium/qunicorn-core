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

from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.provider_name import ProviderName
from tests import test_utils

"""Tests the execution of rigetti. quilc and qvm need to be running in server mode for this test to work"""

IS_ASYNCHRONOUS: bool = False
RESULT_TOLERANCE: int = 100


def test_rigetti_local_simulator_braket_job_results():
    test_utils.execute_job_test(ProviderName.RIGETTI, "2q-qvm", AssemblerLanguage.QASM2)
