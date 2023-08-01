# Copyright 2021 QHAna plugin runner contributors.
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
import logging
from logging import Logger, getLogger

from flask import Flask

ALEMBIC_ENV = "alembic.env"


# originally from <https://github.com/buehlefs/flask-template/>


def get_logger(app: Flask, name: str) -> Logger:
    """Utility method to get a specific logger that is a child logger of the app.logger."""
    logger_name = f"{app.import_name}.{name}"
    return getLogger(logger_name)


def info(message: str):
    logging.getLogger(ALEMBIC_ENV).info(message)


def warn(message: str):
    logging.getLogger(ALEMBIC_ENV).warning(message)


def error(message: str):
    logging.getLogger(ALEMBIC_ENV).error(message, exc_info=True)
