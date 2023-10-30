# Copyright 2023 University of Stuttgart
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

from automapper import mapper

"""General Mapper Class to map from one object to another"""

T = TypeVar("T")


def map_from_to(from_object: object, to_type: Type[T], fields_mapping: dict | None = None) -> T | None:
    """
    This method will automatically map all fields with the same name.
    All fields with different names need to be specified in the fields_mapping dictionary.
    Also, when a field needs to be mapped specifically, with another mapper for example.
    Prevent Null pointers by returning None if the object is none.

    Attributes:
        * from_object: The object that has all the data
        * to_type: The type to create a new object which will get all the data from the "from_object"
        * fields_mapping: A dictionary with the fields as key and the value where it is mapped too
    """

    if from_object is None:
        return None
    return mapper.to(to_type).map(from_object, fields_mapping=fields_mapping)
