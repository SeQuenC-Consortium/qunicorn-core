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

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import sqltypes as sql

from .db_model import DbModel
from ..db import REGISTRY
from ...static.enums.assembler_languages import AssemblerLanguage


@REGISTRY.mapped_as_dataclass
class QuantumProgramDataclass(DbModel):
    """Dataclass for storing QuantumPrograms

    Attributes:
        quantum_circuit (str): Quantum code that needs to be executed.
        assembler_language (enum): Assembler language in which the code should be interpreted.
        id (int): The ID of the quantum program.
        deployment_id (int): The deployment where a list of quantum program is used.
        python_file_path (str): Part of experimental feature: path to file to be uploaded (to IBM).
        python_file_metadata (str): Part of experimental feature: metadata for the python_file.
        python_file_options (str): Part of experimental feature: options for the python_file.
        python_file_input (str): Part of experimental feature: inputs for the python_file.
    """

    # non-default arguments
    quantum_circuit: Mapped[str] = mapped_column(sql.String(500))
    assembler_language: Mapped[str] = mapped_column(sql.Enum(AssemblerLanguage))
    # default arguments
    id: Mapped[int] = mapped_column(sql.INTEGER(), primary_key=True, autoincrement=True, default=None)
    deployment_id: Mapped[int] = mapped_column(
        ForeignKey("Deployment.id", ondelete="CASCADE"), default=None, nullable=True
    )

    # Experimental
    python_file_path: Mapped[str] = mapped_column(sql.String(500), default=None, nullable=True)
    python_file_metadata: Mapped[str] = mapped_column(sql.String(500), default=None, nullable=True)
    python_file_options: Mapped[str] = mapped_column(sql.String(500), default=None, nullable=True)
    python_file_inputs: Mapped[str] = mapped_column(sql.String(500), default=None, nullable=True)
