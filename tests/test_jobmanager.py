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

""""Test class to test the functionality of the job_api"""


# Will be implemented with #47
def test_create_and_run_job():
    """Tests the create job method"""
    """root_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = 'job_test_data.json'
    path_dir = "{}{}{}".format(root_dir, os.sep, file_name)

    with open(path_dir) as f:
        data = json.load(f)

    job: JobDto = namedtuple(JobDto.__name__, data.keys())(*data.values())

    # When no token is added to the json, an error is expected
    if job.token != "":
        result = create_and_run_job(job)

        # Check if Counts are within certain range
        # Assumes total count of 4000
        assert result is not None
        assert 1800 <= int(result["00"]) <= 2200
        assert 1800 <= int(result["11"]) <= 2200
    else:
        with pytest.raises(RuntimeError):
            create_and_run_job(job)"""
