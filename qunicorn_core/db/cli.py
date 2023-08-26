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
import json
import os

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
from .models.result import ResultDataclass
from .models.user import UserDataclass
from ..static.enums.assembler_languages import AssemblerLanguage
from ..static.enums.job_state import JobState
from ..static.enums.job_type import JobType
from ..static.enums.programming_language import ProgrammingLanguage
from ..static.enums.provider_name import ProviderName
from ..util import utils
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
    qc = QuantumProgramDataclass(
        quantum_circuit=utils.get_default_qasm_string(1), assembler_language=AssemblerLanguage.QASM
    )
    qc2 = QuantumProgramDataclass(
        quantum_circuit=utils.get_default_qasm_string(2), assembler_language=AssemblerLanguage.QASM
    )
    qasm3_str: str = "OPENQASM 3; \nqubit[3] q;\nbit[3] c;\nh q[0];\ncnot q[0], q[1];\ncnot q[1], q[2];\nc = measure q;"
    qasm3_program = QuantumProgramDataclass(quantum_circuit=qasm3_str, assembler_language=AssemblerLanguage.QASM)
    braket_str: str = "Circuit().h(0).cnot(0, 1)"
    braket_program = QuantumProgramDataclass(quantum_circuit=braket_str, assembler_language=AssemblerLanguage.BRAKET)

    qiskit_str: str = "global qiskit_circuit; qiskit_circuit = QuantumCircuit(2, 2);qiskit_circuit.h(0);qiskit_circuit.cx(0, 1);qiskit_circuit.measure(0, 0);qiskit_circuit.measure(1, 1)"
    qiskit_program = QuantumProgramDataclass(quantum_circuit=qiskit_str, assembler_language=AssemblerLanguage.QISKIT)

    deployment_ibm_qasm2 = DeploymentDataclass(
        deployed_by=user, programs=[qc, qc2], deployed_at=datetime.datetime.now(), name="DeploymentIBMQasmName"
    )
    deployment_aws_qasm3 = DeploymentDataclass(
        deployed_by=user, programs=[qasm3_program], deployed_at=datetime.datetime.now(), name="DeploymentAWSQasmName"
    )
    deployment_aws_braket = DeploymentDataclass(
        deployed_by=user, programs=[braket_program], deployed_at=datetime.datetime.now(), name="DeploymentAWSBraketName"
    )
    deployment_ibm_qiskit = DeploymentDataclass(
        deployed_by=user, programs=[qiskit_program], deployed_at=datetime.datetime.now(), name="DeploymentIBMQiskitName"
    )

    device_aws, device_ibm = add_devices_and_get_defaults()

    ibm_default_job = JobDataclass(
        executed_by=user,
        executed_on=device_ibm,
        deployment=deployment_ibm_qasm2,
        progress=0,
        state=JobState.READY,
        shots=4000,
        type=JobType.RUNNER,
        started_at=datetime.datetime.now(),
        name="IBMJobName",
        results=[ResultDataclass(result_dict={"0x": "550", "1x": "450"})],
    )

    aws_default_job = JobDataclass(
        executed_by=user,
        executed_on=device_aws,
        deployment=deployment_aws_qasm3,
        progress=0,
        state=JobState.READY,
        shots=4000,
        type=JobType.RUNNER,
        started_at=datetime.datetime.now(),
        name="AWSJobName",
        results=[
            ResultDataclass(
                result_dict={"counts": {"000": 2007, "111": 1993}, "probabilities": {"000": 0.50175, "111": 0.49825}}
            )
        ],
    )

    DB.session.add(ibm_default_job)
    DB.session.add(aws_default_job)
    DB.session.add(deployment_aws_braket)
    DB.session.add(deployment_ibm_qiskit)

    DB.session.commit()
    get_logger(app, DB_COMMAND_LOGGER).info("Test Data loaded.")


def add_devices_and_get_defaults() -> [DeviceDataclass, DeviceDataclass]:
    """Add devices to the database and return the default devices for IBM and AWS"""

    root_dir = os.path.dirname(os.path.abspath(__file__))
    path_dir = "{}{}{}".format(root_dir, os.sep, "qunicorn_devices.json")

    with open(path_dir, "r", encoding="utf-8") as f:
        all_devices = json.load(f)

    provider_aws, provider_ibm = create_provider()

    default_device_aws = None
    default_device_ibm = None

    # iterate over the JSON and add the devices to the database
    for device in all_devices["all_devices"]:
        provider_name: str = device["provider"]
        provider: ProviderDataclass = get_provider_objects_by_name(provider_name, provider_aws, provider_ibm)
        final_device: DeviceDataclass = DeviceDataclass(
            provider_id=provider.id,
            num_qubits=device["num_qubits"],
            device_name=device["name"],
            url="",
            is_simulator=device["is_simulator"],
            provider=provider,
        )

        # Set the default device for IBM and AWS to assign the default-job to this device
        if device["is_default"]:
            if provider_name == ProviderName.IBM:
                default_device_ibm = final_device
            elif provider_name == ProviderName.AWS:
                default_device_aws = final_device

        DB.session.add(final_device)

    return default_device_aws, default_device_ibm


def create_provider() -> [ProviderDataclass, ProviderDataclass]:
    """Create the providers for IBM and AWS and return them"""
    provider_ibm = ProviderDataclass(
        with_token=True,
        supported_language=ProgrammingLanguage.QISKIT,
        name=ProviderName.IBM,
    )
    provider_aws = ProviderDataclass(
        with_token=False,
        supported_language=ProgrammingLanguage.BRAKET,
        name=ProviderName.AWS,
    )
    return provider_aws, provider_ibm


def get_provider_objects_by_name(
    provider_name: str, provider_aws: ProviderDataclass, provider_ibm: ProviderDataclass
) -> ProviderDataclass:
    """Return the provider object by name"""
    if provider_name == ProviderName.AWS:
        return provider_aws
    elif provider_name == ProviderName.IBM:
        return provider_ibm
    raise ValueError(f"Unknown provider name.{provider_name}")


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
