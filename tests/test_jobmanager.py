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
import pathlib

import pytest
from qunicorn_core.api import *
from qunicorn_core.api.jobmanager.jobs import createJob, JobRegister
from collections import namedtuple
import json

""""Test class to test the functionality of the jobmanager"""


def test_create_job():
    """"
    Tests the create job method.
    """
    # Make sure to add a valid token to the jobmanager_test_data.json
    with open('tests/jobmanager_test_data.json') as f:
        data = json.load(f)
    job: JobRegister = namedtuple("JobRegister", data.keys())(*data.values())
    result = createJob(job)

    # Check if Counts are within certain range
    # Assumes total count of 4000
    assert result is not None
    assert 1800 <= int(result["00"]) <= 2200
    assert 1800 <= int(result["11"]) <= 2200

