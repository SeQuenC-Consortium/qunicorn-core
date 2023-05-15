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


"""Module to hold DB constant to avoid circular imports."""

from typing import Type, cast
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy.orm import DeclarativeBase, registry
from sqlalchemy.schema import MetaData


DB: SQLAlchemy = SQLAlchemy(
    metadata=MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(column_0_name)s",
        }
    )
)


# Model constant to be importable directly
MODEL = cast(Type[DeclarativeBase], DB.Model)
if not issubclass(MODEL, Model):
    raise Warning(f"Please update the type cast of db.MODEL to reflect the current type {type(MODEL)}.")

REGISTRY: registry = MODEL.registry

MIGRATE = Migrate()
