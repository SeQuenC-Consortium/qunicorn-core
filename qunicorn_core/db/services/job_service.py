from qunicorn_core.db import DB

session = DB.session

def add_job(job):
    session.add(job)
    session.commit()
    job.id
    session.refresh(job)
    print(job.id)
    return(job.id)

def remove_job(job):
    session.remove(job)
    session.commit()


def get_job(objectDataClass, id):
    return session.get(objectDataClass, id)
