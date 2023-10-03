IBM Pilot
================

The AWS Pilot is used to work with the IBM API.

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

**Notes:** Experimental Feature

**Requires:** A file uploaded to the IBM backend using File Upload.

File Upload
************

**Description:** Uploads a file to the IBM Backend.

**Notes:** Experimental Feature

**Requires:** A .py file to be executed and a corresponding metadata json, needs to follow the standards presented by IBM. Need to be added to the /resources/upload_files folder.
