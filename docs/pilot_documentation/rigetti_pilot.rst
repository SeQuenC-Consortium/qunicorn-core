Rigetti Pilot
================

This site gives an overview of the functionality of the Rigetti Pilot.

The Rigetti Pilot currently allows for local simulation of quantum program, using the pyquil SDK.
Execution on the Rigetti Servers is currently not supported.

Rigetti Pilot furthermore requires the installation of the Rigetti Forest SDK and needs running server instances of
quilc and qvm. Because of this the Rigetti Pilot is currently not available in execution through the docker-compose.


Standard Devices
^^^^^^^^^^^^^^^^^^

The local simulator has the device name: **rigetti_device**

Main Languages
^^^^^^^^^^^^^^^^^^^^

* Quil
**Note:** The transpile manager allows for the use of any language supported by the transpile manager.

Supported Job Types
^^^^^^^^^^^^^^^^^^^^

Runner
*******

**Description:** Execute a simple Job on the local simulator.

**Notes:** Currently only allows for execution on the local simulator.

**Required Language:** Quantum circuit can be provided in: Quil
