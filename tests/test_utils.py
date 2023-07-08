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

""""pytest utils file"""
import json
import os


def get_object_from_json(json_file_name: str):
    """Returns the json object out of the json file with the name json_file_name"""

    root_dir = os.path.dirname(os.path.abspath(__file__))
    path_dir = "{}{}{}".format(root_dir, os.sep, json_file_name)
    with open(path_dir) as f:
        data = json.load(f)
    return data