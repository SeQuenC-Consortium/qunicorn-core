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

""""pytest conftest file"""

from dotenv import load_dotenv

from qunicorn_core import create_app
from qunicorn_core.db.cli import create_db_function, load_db_function

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
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "ENABLE_EXPERIMENTAL_FEATURES": "FALSE",
}


def set_up_env():
    """Set up Flask app and environment and return app"""
    test_config = {}
    test_config.update(DEFAULT_TEST_CONFIG)

    # We need this to load variables from the .env file during testing
    load_dotenv()

    app = create_app(test_config)
    with app.app_context():
        create_db_function(app)
        load_db_function(app)

    return app
