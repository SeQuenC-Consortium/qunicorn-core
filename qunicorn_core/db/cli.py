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
from flask import Flask, Blueprint, current_app

import qunicorn_core.core.pilotmanager.pilot_manager
# make sure all models are imported for CLI to work properly
from . import models  # noqa
from .db import DB
from .models.deployment import DeploymentDataclass
from .models.job import JobDataclass
from .models.quantum_program import QuantumProgramDataclass
from ..static.enums.assembler_languages import AssemblerLanguage
from ..util.logging import get_logger

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
    DB.session.add(create_default_braket_deployment())
    DB.session.add(create_default_qiskit_deployment())
    DB.session.commit()
    qunicorn_core.core.pilotmanager.pilot_manager.save_default_jobs_and_devices_from_provider()
    get_logger(app, DB_COMMAND_LOGGER).info("Test Data loaded.")


def create_default_braket_deployment() -> DeploymentDataclass:
    braket_str: str = "Circuit().h(0).cnot(0, 1)"
    braket_program = QuantumProgramDataclass(quantum_circuit=braket_str, assembler_language=AssemblerLanguage.BRAKET)
    return DeploymentDataclass(
        deployed_by=None, programs=[braket_program], deployed_at=datetime.datetime.now(), name="BraketDeployment"
    )


def create_default_qiskit_deployment() -> DeploymentDataclass:
    qiskit_str: str = (
        "circuit = QuantumCircuit(2, 2);circuit.h(0);" "circuit.cx(0, 1);circuit.measure(0, 0);circuit.measure(1, 1)"
    )
    qiskit_program = QuantumProgramDataclass(quantum_circuit=qiskit_str, assembler_language=AssemblerLanguage.QISKIT)
    return DeploymentDataclass(
        deployed_by=None, programs=[qiskit_program], deployed_at=datetime.datetime.now(), name="QiskitDeployment"
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
