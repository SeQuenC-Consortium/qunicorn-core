AWS Pilot
================

This site gives an overview of the functionality of the AWS Pilot.
The AWS Pilot is used to communicate with AWS Braket, which is the quantum computing service provided by AWS.

The AWS Pilot currently allows for local simulation of quantum program, using the Amazon Braket SDK.
Execution on the AWS Servers is currently not supported.

Standard Devices
^^^^^^^^^^^^^^^^^^

The local simulator has the device name: **local_simulator**

Main Languages
^^^^^^^^^^^^^^^^^^^^

* Braket
* QASM 3

**Note:** The transpile manager allows for the use of any language supported by the transpile manager.

Supported Job Types
^^^^^^^^^^^^^^^^^^^^

Runner
*******

**Description:** Execute a simple Job on the local simulator.

**Notes:** Currently only allows for execution on the local simulator.

**Required Language:** Quantum circuit can be provided in: Braket, QASM3

