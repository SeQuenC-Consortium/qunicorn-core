# Copyright 2023 University of Stuttgart.
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

# originally from <https://github.com/buehlefs/flask-template/>


"""CLI functions for the db module."""

import click
from flask import Flask, Blueprint, current_app

# make sure all api_models are imported for CLI to work properly
from . import models  # noqa
from .db import DB
from .models.device import DeviceDataclass
from .models.provider import ProviderDataclass
from .models.user import UserDataclass
from ..static.enums.programming_language import ProgrammingLanguage
from ..static.enums.provider_name import ProviderName
from ..util.logging import get_logger

DB_CLI_BLP = Blueprint("db_cli", __name__, cli_group=None)
DB_CLI = DB_CLI_BLP.cli  # expose as attribute for autodoc generation

DB_COMMAND_LOGGER = "db"


@DB_CLI.command("create-and-load-db")
def create_load_db():
    """Create all db tables."""
    create_db_function(current_app)
    load_db_function(current_app)
    click.echo("Database created and loaded.")


@DB_CLI.command("create-db")
def create_db():
    """Create all db tables."""
    create_db_function(current_app)
    click.echo("Database created.")


def create_db_function(app: Flask):
    DB.create_all()
    get_logger(app, DB_COMMAND_LOGGER).info("Database created.")


@DB_CLI.command("load-test-data")
def load_test_data():
    """Load database test data"""
    load_db_function(current_app)
    click.echo("Test Data Loaded.")


def load_db_function(app: Flask):
    provider = ProviderDataclass(
        with_token=True,
        supported_language=ProgrammingLanguage.QISKIT,
        name=ProviderName.IBM,
    )
    DB.session.add(provider)
    DB.session.commit()
    DB.session.refresh(provider)
    device = DeviceDataclass(provider=provider, rest_endpoint="")
    DB.session.add(device)
    DB.session.commit()
    user = UserDataclass(name="Default User")
    DB.session.add(user)
    DB.session.commit()
    get_logger(app, DB_COMMAND_LOGGER).info("Test Data loaded.")


@DB_CLI.command("drop-db")
def drop_db():
    """Drop all db tables."""
    drop_db_function(current_app)
    click.echo("Database dropped.")


def drop_db_function(app: Flask):
    DB.drop_all()
    get_logger(app, DB_COMMAND_LOGGER).info("Dropped Database.")


def register_cli_blueprint(app: Flask):
    """Method to register the DB CLI blueprint."""
    app.register_blueprint(DB_CLI_BLP)
    app.logger.info("Registered blueprint.")
