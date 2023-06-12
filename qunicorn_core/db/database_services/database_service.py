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
from qunicorn_core.db import DB

session = DB.session


def save_database_object(db_object) -> object:
    session.add(db_object)
    session.commit()
    session.refresh(db_object)
    return db_object


def remove_database_object(db_object):
    session.remove(db_object)
    session.commit()


def get_database_object(database_object_class, db_object_id):
    return session.get(database_object_class, db_object_id)


def get_session():
    return session
