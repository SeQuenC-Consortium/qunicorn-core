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


def add_database_object(object):
    session.add(object)
    session.commit()
    session.refresh(object)
    return object.id


def remove_database_object(object):
    session.remove(object)
    session.commit()


def get_database_object(database_object_class, database_id):
    return session.get(database_object_class, database_id)
