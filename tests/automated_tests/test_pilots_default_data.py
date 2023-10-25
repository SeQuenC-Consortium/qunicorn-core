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

"""Test in-request execution for aws"""

from qunicorn_core.core.pilotmanager import pilot_manager
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.provider import ProviderDataclass


def test_pilots_default_job_deployment():
    """Test for each pilot if the default job and deployment is correctly created"""
    for pilot in pilot_manager.PILOTS:
        # GIVEN: The pilot is set up correctly
        assert pilot.supported_languages is not None
        assert pilot.provider_name is not None

        # WHEN: Getting the standard job
        device_list_without_default, default_device = pilot.get_standard_devices()
        job: JobDataclass = pilot.get_standard_job_with_deployment(default_device)

        # THEN: The job is created correctly
        assert default_device.provider.name == pilot.provider_name
        assert job.executed_on == default_device
        assert len(job.deployment.programs) > 0
        assert job.deployment.programs[0].assembler_language == pilot.supported_languages[0]
        assert job.deployment.programs[0].quantum_circuit is not None


def test_pilots_default_provider():
    """Test for each pilot if the default provider is correctly created"""
    for pilot in pilot_manager.PILOTS:
        # GIVEN: The pilot is set up correctly
        assert pilot.provider_name is not None

        # WHEN: Getting the standard provider
        provider: ProviderDataclass = pilot.get_standard_provider()

        # THEN: The Provider is created correctly
        assert provider is not None
        assert len(provider.supported_languages) == len(pilot.supported_languages)
        assert len(pilot.supported_languages) > 0 and len(provider.supported_languages) > 0
        assert provider.name == pilot.provider_name
