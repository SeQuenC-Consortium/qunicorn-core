from qunicorn_core.api.api_models import JobCoreDto, DeviceDto
from qunicorn_core.core.pilotmanager.base_pilot import Pilot
from qunicorn_core.db.models.device import DeviceDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.result import ResultDataclass
from qunicorn_core.db.models.user import UserDataclass
from qunicorn_core.static.enums.assembler_languages import AssemblerLanguage
from qunicorn_core.static.enums.provider_name import ProviderName
from qunicorn_core.util import logging
from pyquil import get_qc


class RigettiPilot(Pilot):
    """The AWS Pilot"""

    provider_name: ProviderName = ProviderName.RIGETTI

    supported_languages: list[AssemblerLanguage] = [AssemblerLanguage.QUIL]

    def run(self, job_core_dto: JobCoreDto) -> list[ResultDataclass]:
        """Execute the job on a local simulator and saves results in the database"""
        qc = get_qc("3q-qvm")
        executable = qc.compile(job_core_dto.transpiled_circuits)
        result = qc.run(executable)

    def execute_provider_specific(self, job_core_dto: JobCoreDto):
        """Execute a job of a provider specific type on a backend using a Pilot"""


    def cancel_provider_specific(self, job_dto):
        logging.warn(
            f"Cancel job with id {job_dto.id} on {job_dto.executed_on.provider.name} failed."
            f"Canceling while in execution not supported for AWS Jobs"
        )
        raise ValueError("Canceling not supported on AWS devices")

    def get_standard_job_with_deployment(self, user: UserDataclass, device: DeviceDataclass) -> JobDataclass:
        """Get the standard job including its deployment for a certain user and device"""

    def save_devices_from_provider(self, device_request):
        """
        Save the available aws device into the database.
        Since there is currently only a local simulator in use, the device_request parameter is unused.
        """
    def get_standard_provider(self):

    def is_device_available(self, device: DeviceDto, token: str) -> bool:
        logging.info("AWS local simulator is always available")
        return True
