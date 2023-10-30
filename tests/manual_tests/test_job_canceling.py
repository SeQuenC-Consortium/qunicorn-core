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

"""A guide how to test the cancel and queue feature of qunicorn

For this feature we need a broker and qunicorn running.
Thus, it is not possible to test this automatically, because asynchronous tasks are not supported by our pytest setting.

# GIVEN:
1. Start qunicorn with the env. Variable EXECUTE_CELERY_TASK_ASYNCHRONOUS=True
2. Start Docker
3. Start the broker (poetry run invoke broker and poetry run invoke start-broker)
4. Make sure to add your ibm token to the env file

# WHEN:
5. Use the Qunicorn API to create three jobs (change the device name to "ibmq_qasm_simulator" to have a slower job)
6. Use the Qunicorn API to cancel the last job (you get the id from the previous response)
7. Use the Qunicorn API to get the job queue

# THEN:
    -> As a response the job-state should be CANCELED
    - One running and multiple queued jobs should be returned when accessing the endpoint
    - All jobs except the canceled job should be finished at the end
    - The jobs are executed in FIFO order

"""
