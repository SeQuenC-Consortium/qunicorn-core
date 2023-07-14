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

""""Test class to test the functionality of the job_api"""

from qunicorn_core.api.api_models import QuantumProgramDto
from qunicorn_core.core.programmanager import programmanager_service
from qunicorn_core.db.models.quantum_program import QuantumProgramDataclass
from tests.conftest import set_up_env
from tests.test_utils import get_object_from_json


def test_create_program():
    """Testing the creation of a quantum program"""
    # GIVEN: Setting up Mocks and Environment
    app = set_up_env()
    quantum_program_dto: QuantumProgramDto = QuantumProgramDto(**get_object_from_json("program_request_dto_test_data.json"))

    # WHEN: Executing method to be tested
    with app.app_context():
        result_program: QuantumProgramDataclass = programmanager_service.create_database_program(quantum_program_dto)

    # THEN: Test Assertion
    with app.app_context():
        assert result_program.id is not None
        assert result_program.python_file_path == "hello.py"
        assert result_program.python_file_inputs == '{"my_obj": "MyCustomClass(my foo, my bar)"}'
        assert result_program.python_file_metadata == "hello.json"
        assert result_program.python_file_options == '{"backend": "ibmq_qasm_simulator"}'
        assert result_program.assembler_language == "QASM"
