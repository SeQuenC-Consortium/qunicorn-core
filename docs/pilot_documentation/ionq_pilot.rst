IonQ Pilot
================

This site gives an overview of the functionality of the IonQ Pilot.
The IonQ Pilot is used to communicate with the IonQ Quantum Cloud, which is the quantum computing service provided by IonQ.

The IonQ Pilot allows for local simulation using the IBM AerSimulator or execution on the IonQ Quantum Computing Servers.
It uses the Qiskit SDK for its implementation.
Execution on IonQ Quantum Computing requires an IonQ Quantum Cloud account, as well as an Access Token.
This can be created free of charge, however certain backends and devices require a paid subscription.
Possible are execution on a simulator as well as real hardware. The execution on a simulator is until now only possible on an ideal simulator without noise.

Standard Devices
^^^^^^^^^^^^^^^^^^

The local simulator has the device name: **aer_simulator**

Main Languages
^^^^^^^^^^^^^^^^^^^^

* QISKIT

**Note:** The transpile manager allows for the use of any language supported by the transpile manager.

Supported Job Types
^^^^^^^^^^^^^^^^^^^^

Runner
*******

**Description:** Execute a job locally using aer_simulator or on a IonQ backend.

**Notes:** For execution on aer_simulator use a local backend. For execution on a IonQ backend use a remote backend.

