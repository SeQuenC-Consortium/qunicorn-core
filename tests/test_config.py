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

""""Test class to test the functionality of the job_api"""
import os
from pathlib import Path

from qunicorn_core import create_app
from qunicorn_core.db.cli import create_db_function, load_db_function, drop_db_function

DEFAULT_TEST_CONFIG = {
    "SECRET_KEY": "test",
    "DEBUG": False,
    "TESTING": True,
    "JSON_SORT_KEYS": True,
    "JSONIFY_PRETTYPRINT_REGULAR": False,
    "DEFAULT_LOG_FORMAT_STYLE": "{",
    "DEFAULT_LOG_FORMAT": "{asctime} [{levelname:^7}] [{module:<30}] {message}    <{funcName}, {lineno}; {pathname}>",
    "DEFAULT_FILE_STORE": "local_filesystem",
    "FILE_STORE_ROOT_PATH": "files",
    "OPENAPI_VERSION": "3.0.2",
    "OPENAPI_JSON_PATH": "api-spec.json",
    "OPENAPI_URL_PREFIX": "",
}


# @pytest.fixture
def set_up_env():
    print("SETTING UP ENVIRONMENT FOR TESTS")
    test_config = {}
    test_config.update(DEFAULT_TEST_CONFIG)
    test_config.update(
        {"SQLALCHEMY_DATABASE_URI": f"sqlite:///" + os.path.join(str(Path(".").absolute()), "qunicorn_test_db")})
    app = create_app(test_config=test_config)
    with app.app_context():
        drop_db_function(app)
        create_db_function(app)
        load_db_function(app)

    return app
