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
import datetime

import click
from flask import Blueprint, Flask, current_app

import qunicorn_core.core.pilotmanager.pilot_manager

from .db import DB
from .models.deployment import DeploymentDataclass
from .models.job import JobDataclass
from .models.provider import ProviderDataclass
from .models.quantum_program import QuantumProgramDataclass
from ..static.enums.assembler_languages import AssemblerLanguage
from ..util import utils
from ..util.logging import get_logger

# make sure all models are imported for CLI to work properly
from . import models  # noqa

DB_CLI_BLP = Blueprint("db_cli", __name__, cli_group=None)
DB_CLI = DB_CLI_BLP.cli  # expose as attribute for autodoc generation
DB_COMMAND_LOGGER = "db"


@DB_CLI.command("recreate-and-load-db")
def recreate_and_load_db():
    """(Re-)create all db tables."""
    drop_db_function(current_app)
    create_db_function(current_app)
    load_db_function(current_app)
    click.echo("Database created and loaded.")


@DB_CLI.command("create-and-load-db")
def create_and_load_db():
    """Create all db tables and load testdata."""
    create_db_function(current_app)
    load_db_function(current_app)
    click.echo("Database created.")


def create_db_function(app: Flask):
    DB.create_all()
    get_logger(app, DB_COMMAND_LOGGER).info("Database created.")


@DB_CLI.command("load-providers")
def load_providers():
    """Load provider data into the database."""
    load_providers_db_function(current_app, if_not_exists=False)
    click.echo("Provider Data Loaded.")


def load_providers_db_function(app: Flask, if_not_exists=True):
    db_is_empty = not ProviderDataclass.get_all()
    if if_not_exists and not db_is_empty:
        return

    # Save all default data from the pilots
    qunicorn_core.core.pilotmanager.pilot_manager.save_default_jobs_and_devices_from_provider(
        include_default_jobs=False
    )
    get_logger(app, DB_COMMAND_LOGGER).info("Test Data loaded.")


@DB_CLI.command("load-test-data")
def load_test_data():
    """Load database test data"""
    load_db_function(current_app, if_not_exists=False)
    click.echo("Test Data Loaded.")


def load_db_function(app: Flask, if_not_exists=True):
    db_is_empty = DB.session.query(JobDataclass).first() is None
    if if_not_exists and not db_is_empty:
        return

    # Create default deployments for languages that do not have their own primary pilot.
    DB.session.add(create_default_qasm2_deployment())
    DB.session.add(create_default_qasm3_deployment())
    DB.session.commit()

    # Save all default data from the pilots
    qunicorn_core.core.pilotmanager.pilot_manager.save_default_jobs_and_devices_from_provider()
    get_logger(app, DB_COMMAND_LOGGER).info("Test Data loaded.")


def create_default_qasm2_deployment() -> DeploymentDataclass:
    language = AssemblerLanguage.QASM2
    program = QuantumProgramDataclass(quantum_circuit=utils.get_default_qasm2_string(1), assembler_language=language)
    DB.session.add(program)
    return DeploymentDataclass(
        deployed_by=None,
        programs=[program],
        deployed_at=datetime.datetime.now(),
        name="QASM2Deployment",
    )


def create_default_qasm3_deployment() -> DeploymentDataclass:
    language = AssemblerLanguage.QASM3
    qasm3_str: str = (
        "OPENQASM 3; \nqubit[3] q;\nbit[3] c;\nh q[0];\ncnot q[0], q[1];\ncnot q[1], q[2];\nc = " "measure q;"
    )
    program = QuantumProgramDataclass(quantum_circuit=qasm3_str, assembler_language=language)
    DB.session.add(program)
    return DeploymentDataclass(
        deployed_by=None, programs=[program], deployed_at=datetime.datetime.now(), name="QASM3Deployment"
    )


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
