from datetime import datetime

from qunicorn_core.db.database_services import database_service
from qunicorn_core.db.models.job import JobDataclass


def add_database_job(job):
    return database_service.add_database_object(JobDataclass(data=job.circuit, state="1", progress=0,
                                                                    started_at=datetime.now()))
