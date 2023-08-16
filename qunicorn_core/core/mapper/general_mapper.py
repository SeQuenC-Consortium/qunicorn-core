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

T = TypeVar("T")


def map_from_to(from_object: object, to_type: Type[T], fields_mapping: dict | None = None) -> T | None:
    if from_object is None:
        return None
    return mapper.to(to_type).map(from_object, fields_mapping=fields_mapping)
