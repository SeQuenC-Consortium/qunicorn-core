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
from qiskit import QuantumCircuit

# make sure all api_models are imported for CLI to work properly
from . import models  # noqa
from .db import DB
from .models.deployment import DeploymentDataclass
from .models.device import DeviceDataclass
from .models.job import JobDataclass
from .models.provider import ProviderDataclass
from .models.quantum_program import QuantumProgramDataclass
from .models.user import UserDataclass
from ..static.enums.job_state import JobState
from ..static.enums.programming_language import ProgrammingLanguage
from ..static.enums.provider_name import ProviderName
from ..util.logging import get_logger

DB_CLI_BLP = Blueprint("db_cli", __name__, cli_group=None)
DB_CLI = DB_CLI_BLP.cli  # expose as attribute for autodoc generation

DB_COMMAND_LOGGER = "db"


@DB_CLI.command("create-and-load-db")
def create_load_db():
    """Create all db tables."""
    drop_db_function(current_app)
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


def get_quasm_string() -> str:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc.qasm()


def load_db_function(app: Flask):
    user = UserDataclass(name="DefaultUser")
    qc = QuantumProgramDataclass(quantum_circuit=get_quasm_string())
    deployment = DeploymentDataclass(deployed_by=user, quantum_program=qc, deployed_at=datetime.datetime.now(), name="DeploymentName")
    provider = ProviderDataclass(
        with_token=True,
        supported_language=ProgrammingLanguage.QISKIT,
        name=ProviderName.IBM,
    )
    device = DeviceDataclass(provider=provider, url="")
    job = JobDataclass(
        executed_by=user,
        executed_on=device,
        deployment=deployment,
        progress=0,
        state=JobState.READY,
        shots=4000,
        started_at=datetime.datetime.now(),
        name="JobName",
    )
    DB.session.add(job)
    DB.session.commit()
    user = UserDataclass(name="DefaultUser")
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
