from qunicorn_core.api.jobmanager.job_pilots import QiskitPilot, AWSPilot
from qunicorn_core.celery import CELERY

qiskitpilot = QiskitPilot
awspilot = AWSPilot


@CELERY.task()
def create_and_run_job(job_dto, job_id):
    """Create a job and assign to the target pilot"""

    if job_dto.provider == 'IBMQ':
        pilot = qiskitpilot("QP")
        pilot.execute(job_dto, job_id)
    else:
        print("No valid target specified")
    return 0
