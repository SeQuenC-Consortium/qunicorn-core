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

"""A guide how to perform a load test on qunicorn with postman

For this test a running instance of the qunicorn docker-compose is necessary.
Also, postman needs to be installed. (Download under: https://www.postman.com/downloads/)
The Postman collection provided is testing the POST Deployment and Job Endpoint.

# GIVEN:
1. Start qunicorn using the docker-compose.
2. Start postman.
3. Open a workspace.
4. Import the collection called "Qunicorn_High_Load_Test.postman-collection" provided under test_resources.

# WHEN:
5. Select the Collection and Press on "Run collection".
6. Under "Runner" select "Performance" on the right.
7. Choose a number of virtual users and the test duration.
8. Press on Run

# THEN:
    -> Postman will show you how the test is performing.
    -> After the Test has concluded, check the qunicorn database whether all deployments and jobs have been created
    and the jobs have finished.

"""
