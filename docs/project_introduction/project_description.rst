Project Description
====================

Qunicorn is used as a unification layer.
Users can create deployments to deploy/register their quantum programs at qunicorn.
These deployments can be referenced when creating jobs.
Jobs are used to run the quantum programs defined in the deployments on the quantum hardware.
The quantum hardware is provided by different providers like AWS and IBM.
    .. image:: ../resources/images/qunicorn_overview.png


Circuit Transpilation
---------------------
The qunicorn application is used to transpile circuits between different assembler languages.
For example is it possible to run a braket-circuit on IBM when using the qunicorn application.
Generally it is not possible to directly run a braket-circuit on IBM, the circuit first needs to be transpiled to QISKIT.


Job Queuing
-----------
When multiple user want to execute multiple jobs on qunicorn, these jobs need to be queued because not all jobs can be run in parallel.
Therefor a celery queue and pilots are used.
A pilot is responsible for one provider and is used to run jobs on the quantum hardware of that provider.
The celery queue is used to queue jobs and to distribute them over the pilots.


Persist Jobs & Deployment
-------------------------
Qunicorn is used to store the jobs and their results to be accessed later.
Not only the Jobs and Deployments are stored, but also all possible providers and possible devices of these providers.


Authentication with UserManagement
----------------------------------
Qunicorn uses Keycloak to authenticate users.
Keycloak is an open source software to manage users and their roles.
A user can generate a token for himself, which will be checked in qunicorn.
If a user creates a job or deployment with his token, this job will not be accessible for other users.


Connection to Workflow Management
---------------------------------
Qunicorns REST-API can be used to create jobs and deployments.
Therefor it is possible to access qunicorn from the workflow modeller which uses RestEndpoints. https://github.com/PlanQK/workflow-modeler
Together with the workflow modeller UseCases can be generated to test qunicorn.
In this repository one can find some example UseCases and how to generate them: https://github.com/SeQuenC-Consortium/SeQuenC-UseCases
