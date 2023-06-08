import pytest
from qunicorn_core.api import *
from qunicorn_core.api.jobmanager.jobs import createJob, JobRegister
from collections import namedtuple
import json

def test_create_job():
    # Make sure to add a valid token to the test_data.json
    f = open("test_data.json")
    new_job_data = json.load(f)
    job: JobRegister = namedtuple("JobRegister", new_job_data.keys())(*new_job_data.values())
    result = createJob(job)

    # Check if Counts are within certain range
    # Assumes total count of 4000
    assert result is not None
    assert 1800 <= int(result["00"]) <= 2200
    assert 1800 <= int(result["11"]) <= 2200

