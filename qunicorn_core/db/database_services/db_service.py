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
from typing import TypeVar, Type

from qunicorn_core.db import DB
from qunicorn_core.db.models.db_model import DbModel

"""Module containing all general database requests"""

session = DB.session
DbModelType = TypeVar("DbModelType", bound=DbModel)
DbModelTypes = TypeVar("DbModelTypes", bound=list[DbModel])


def save_database_object(db_object: DbModel) -> DbModelType:
    """Creates or Updates a database object, as long as it is a database-model"""
    session.add(db_object)
    session.commit()
    session.refresh(db_object)
    return db_object


def remove_database_object_by_id(db_object: Type[DbModel], id: int):
    """Deletes a database object, as long as it is a database-model"""
    session.query(db_object).filter_by(id=id).delete()
    session.commit()


def get_database_object(db_object_id: int, database_object_class: Type[DbModel]) -> DbModelType:
    """Gets a database object

    Arguments:
        db_object_id            - id of the database object
        database_object_class   - class of the database object
    """
    return session.get(database_object_class, db_object_id)


def get_all_database_objects(database_object_class: Type[DbModel]) -> DbModelTypes:
    """Gets all database objects of a table

    Arguments:
        database_object_class   - class of the database objects
    """
    return session.query(database_object_class).all()


def get_session():
    return session
