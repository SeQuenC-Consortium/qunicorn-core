Current Functionality
######################

To give a brief overview of the current functionality of the application.
The user currently has one main way to access the application, this is through the defined API Endpoints.

A good way to get an overview, as well as example values, is to access those through the Swagger UI.

The Endpoints defined can be found on the api documentation under :doc:`my document <../architecture_documentation/api_documentation/apidocumentation>`.

Available Providers
#####################
Currently the following providers are available:

* IBMQ:
   * Base languages:
        * QASM
        * Qiskit
   * Available Job Types:
        * RUNNER
        * ESTIMATOR
        * SAMPLER
   * Experimental Job Types:
        * IBM_UPLOAD (Uploads a Job to the IBM Backend)
        * IBM_RUNNER (Runs a previously uploaded job from the IBM Backend)

* AWS
    * Base languages:
        * QASM
        * BRAKET
    * Available Functions
        * RUNNER

Please note that this list is not exhaustive and will be updated as more providers are added.


Supported Languages
####################

Qunicorn supports a vast array of different programming and assembler languages in the context of quantum computing.

Assembler languages:
^^^^^^^^^^^^^^^^^^^^
* QASM
* Braket
* Python
* Qrisp
* BasiQ

Please note that this list is not exhaustive and will be updated as more assembler languages are added.

Programming languages:
^^^^^^^^^^^^^^^^^^^^^^

* Qiskit
* PyQuil
* QMWare
* Braket

Please note that this list is not exhaustive and will be updated as more programming languages are added.

Job Types:
^^^^^^^^^^

The following Job Types are currently available, check with the provider for more information on the specific job types.

