Rigetti Pilot
================

This site gives an overview of the functionality of the Rigetti Pilot.

The Rigetti Pilot is implemented in an experimental form, and currently allows for local simulation of quantum program, using the pyquil SDK.
Execution on the Rigetti Servers is currently not supported.

The Pilot furthermore requires the installation of the Rigetti Forest SDK and needs running server instances of
quilc and qvm. Because of this, the Rigetti Pilot is currently not available in execution through the docker-compose.
The execution is disabled when running on docker.

Check the following page for information on how to start rigetti locally: :doc:`Getting started <../tutorials/getting_started>`

Standard Devices
^^^^^^^^^^^^^^^^^^

The local simulator has the device name: **rigetti_device**

Main Languages
^^^^^^^^^^^^^^^^^^^^

* Quil

**Note:** The transpile manager is only available in experimental form for this pilot.

Supported Job Types
^^^^^^^^^^^^^^^^^^^^

Runner
*******

**Description:** Execute a simple Job on the local simulator.

**Notes:** Currently only allows for execution on the local simulator.

**Required Language:** Quantum circuit can be provided in: Quil
