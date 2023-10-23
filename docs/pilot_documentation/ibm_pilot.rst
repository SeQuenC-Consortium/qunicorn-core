IBM Pilot
================

This site gives an overview of the functionality of the IBM Pilot.
The IBM Pilot is used to communicate with IBM Quantum Computing, which is the quantum computing service provided by IBM.

The IBM Pilot allows for local simulation using the IBM AerSimulator or execution on the IBM Quantum Computing Servers.
It uses the Qiskit SDK for its implementation.
Execution on IBM Quantum Computing requires an IBM Quantum Computing account, as well as an Access Token.
This can be created free of charge, however certain backends and devices require a paid subscription.

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

**Description:** Execute a job locally using aer_simulator or on a IBM backend.

**Notes:** For execution on aer_simulator use a local backend. For execution on a IBM backend use a remote backend.

Estimator
*********

**Description:** Uses the Estimator to execute a job on an IBM backend.

**Notes:**  Can also be executed locally using LocalEstimator.

Sampler
********

**Description:** Uses the Sampler to execute a job on an IBM backend.

**Notes:** Can also be executed locally using LocalSampler.

File Runner
***********

**Description:** Executes files already uploaded to the IBM Backend using their id.

**Notes:** Experimental Feature. Could not be fully tested due to missing authorization to the IBM Backend. It should be used with Caution. Needs to be enabled by setting ENABLE_EXPERIMENTAL_FEATURES to True.

**Requires:** A file uploaded to the IBM backend using File Upload.

File Upload
************

**Description:** Uploads a file to the IBM Backend.

**Notes:** Experimental Feature. Could not be fully tested due to missing authorization to the IBM Backend. It should be used with Caution. Needs to be enabled by setting ENABLE_EXPERIMENTAL_FEATURES to True.

**Requires:** A .py file to be executed and a corresponding metadata json, needs to follow the standards presented by IBM. Need to be added to the /resources/upload_files folder.
