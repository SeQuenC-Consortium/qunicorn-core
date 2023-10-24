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

"""Module containing default config values."""
from logging import WARNING, INFO
from os import urandom

from .celery_config import CELERY_DEBUG_CONFIG
from .smorest_config import SmorestProductionConfig, SmorestDebugConfig
from .sqlalchemy_config import SQLAchemyProductionConfig, SQLAchemyDebugConfig


class ProductionConfig(SQLAchemyProductionConfig, SmorestProductionConfig):
    ENV = "production"
    SECRET_KEY = urandom(32)

    REVERSE_PROXY_COUNT = 0

    DEBUG = False
    TESTING = False

    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    LOG_CONFIG = None  # if set this is preferred

    DEFAULT_LOG_SEVERITY = WARNING
    DEFAULT_LOG_FORMAT_STYLE = "{"
    DEFAULT_LOG_FORMAT = (
        "{asctime} [{levelname:^7}] [{module:<15}] {message:<175}    <{funcName}, {lineno}; {pathname}>"
    )
    DEFAULT_LOG_DATE_FORMAT = None

    CELERY = CELERY_DEBUG_CONFIG


class DebugConfig(ProductionConfig, SQLAchemyDebugConfig, SmorestDebugConfig):
    ENV = "development"
    DEBUG = True
    SECRET_KEY = "debug_secret"  # FIXME make sure this NEVER! gets used in production!!!

    CELERY = CELERY_DEBUG_CONFIG

    DEFAULT_LOG_SEVERITY = INFO
