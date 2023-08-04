Glossary
========

**Qunicorn**:
The name of the this application that serves as an API for quantum computing request.

**Job**:
The data object that is used to run deployments with their quantum programs on specified provider and store their results

**Deployment**:
The data object that stores information about quantum programs and their configurations.
Is used to register/deploy them, to use them later in multiple jobs.

**Provider**:
An institution that provides quantum computer or simulators.

**Device**:
A single quantum computer that belongs to a provider

**Pilots**:
They are run in a celery-task and are used to communicate with the provider apis and run the jobs there.

**Service**:
Files that belong to the service-layer or core. They calculate or process data, but do not directly communicate with the database.

**QASM-Format**:
The most used format to describe quantum circuits.

**CLI**: Shortcut for command line interface, used to initially set up the database with custom commands.

**Celery**:
A python library that is used to run tasks in the background. It is used to run the quantum programs on the quantum computers.

**Worker**:
Used as a synonym for a celery worker. That is a process that executes tasks in the background.

**Broker**:
Used in the context of celery and docker. Managed die Celery Worker.

**In-Request**:
Something that is done in a request. For example in-request-execution means that the execution of a quantum program is done in the request.

