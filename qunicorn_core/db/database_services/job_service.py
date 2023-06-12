from datetime import datetime

from qunicorn_core.db.database_services import database_service
from qunicorn_core.db.models.job import Job
from qunicorn_core.static.enums.job_state import JobState
from sqlalchemy import update as sqlalchemy_update


def create_database_job(job):
    db_job: Job = Job(data=job.circuit, state=JobState.READY, progress=0, started_at=datetime.now())
    return database_service.save_database_object(db_job)


def update_attribute(job_id: int, job_state: JobState, attribute_name):
    database_service.get_session().query(Job).filter(Job.id == job_id).update({attribute_name: job_state})
    database_service.get_session().commit()


def update_result_and_state(job_id: int, job_state: JobState, results):
    database_service.get_session()\
        .query(Job)\
        .filter(Job.id == job_id)\
        .update({Job.state: job_state, Job.results: results})
    database_service.get_session().commit()
