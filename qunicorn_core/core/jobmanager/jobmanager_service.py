from qunicorn_core.api.jobmanager.job_pilots import QiskitPilot, AWSPilot
from qunicorn_core.celery import CELERY

qiskitpilot = QiskitPilot
awspilot = AWSPilot


@CELERY.task()
def create_and_run_job(job_dto):
    """Create a job and assign to the target pilot which executes the job"""

    if job_dto.provider == 'IBMQ':
        pilot = qiskitpilot("QP")
        pilot.execute(job_dto)
    else:
        print("No valid target specified")
    return 0
