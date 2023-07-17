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
from datetime import datetime

from qunicorn_core.db.database_services import db_service
from qunicorn_core.db.models.deployment import DeploymentDataclass
from qunicorn_core.db.models.job import JobDataclass
from qunicorn_core.db.models.user import UserDataclass


# originally from <https://github.com/buehlefs/flask-template/>


def create(deployment: DeploymentDataclass) -> DeploymentDataclass:
    """Creates a database job with the given circuit and saves it in the database"""
    default_user: UserDataclass = db_service.get_database_object(1, UserDataclass)
    deployment.deployed_by = default_user
    deployment.deployed_at = datetime.now()
    return db_service.save_database_object(deployment)


def get_all_deployments() -> list[DeploymentDataclass]:
    """Gets the Deployment with the deployment_id from the database"""
    return db_service.get_all_database_objects(DeploymentDataclass)


def delete(id: int) -> DeploymentDataclass:
    """Removes one deployment"""

    return db_service.delete_database_object_by_id(DeploymentDataclass, id)


def get_deployment(deployment_id: int) -> JobDataclass:
    """Gets the Deployment with the deployment_id from the database"""
    return db_service.get_database_object(deployment_id, DeploymentDataclass)
