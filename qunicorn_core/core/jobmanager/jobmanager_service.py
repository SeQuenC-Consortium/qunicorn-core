from qunicorn_core.api.jobmanager.job_pilots import QiskitPilot, AWSPilot
from qunicorn_core.api.jobmanager.job_dto import JobDto
from qunicorn_core.celery import CELERY

qiskitpilot = QiskitPilot
awspilot = AWSPilot


@CELERY.task()
def create_and_run_job(job_dto_dict: dict):
    """Create a job and assign to the target pilot which executes the job"""

    job_dto: JobDto = JobDto(**job_dto_dict)

    if job_dto.provider == 'IBMQ':
        pilot = qiskitpilot("QP")
        pilot.execute(job_dto)
    else:
        print("No valid target specified")
    return 0
