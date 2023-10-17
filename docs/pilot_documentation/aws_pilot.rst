AWS Pilot
================

This site gives an overview of the functionality of the AWS Pilot.
The AWS Pilot is used to communicate with AWS Braket, which is the quantum computing service provided by AWS.

Supports local execution.


Standard Devices
^^^^^^^^^^^^^^^^^^

The local simulator has the device name: **local_simulator**
Set this as the name in the requests.

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

