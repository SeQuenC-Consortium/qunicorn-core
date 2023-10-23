Database Models
=========================================

Deployment
----------------------

Attributes of Deployment Data

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - id
        - int 
        - The id of a deployment.

    *   - deployed_by
        - str
        - The user_id that deployed this deployment.
        
    *   - programs
        - list
        - A list of quantum programs.
        
    *   - deployed_at
        - Date 
        - Date of the creation of the object.

    *   - name
        - str
        - The name of the deployment.
   
=====

Device
--------------

Attributes of Device Data

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - id
        - int
        - Automatically generated database id. Use the id to fetch this information from the database.

    *   - provider_id
        - int
        - provider_id of the provider saved in the provider table.

    *   - num_qubits
        - int
        - The amount of qubits that is available at this device.

    *   - name
        - str
        - The name of the device.

    *   - is_simulator
        - int
        - The information whether the device is a simulator (true) or not (false).

    *   - is_local
        - int
        - The information whether jobs executed on this device are executed local or not.

=====

Job
----------------------

Attributes of Job Data

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - id
        - int 
        - Automatically generated database id. Use the id to fetch this information from the database.

    *   - executed_by
        - str (optional) 
        - A user_id associated to the job, user that wants to execute the job.

    *   - executed_on_id
        - str 
        - The device_id of the device where the job is running on.

    *   - deployment_id
        - int 
        - A deployment_id associated with the job

    *   - progress
        - float
        - The progress of the job.

    *   - state
        - str (optional)
        - The state of a job, enum JobState.

    *   - shots
        - int
        - The number of shots for the job.

    *   - type
        - JobType
        - The type of the job.

    *   - started_at
        - Date (optional)
        - The moment the job was scheduled. (default :py:func:`~datetime.datetime.utcnow`)

    *   - finished_at
        - Date (optional)
        - The moment the job finished successfully or with an error.

    *   - name
        - str (optional)
        - Optional name for a job.

    *   - provider_specific_id
        - str (optional)
        - The provider specific id for the job. (Used for canceling)

    *   - celery_id
        - str (optional)
        - The celery id for the job. (used for canceling)


Provider
--------

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - id
        - int
        - The id of a provider.

    *   - with_token
        - bool
        - If authentication is needed and can be done by passing a token this attribute is true.

    *   - name
        - str
        - Name of the cloud service.


=====

Provider Assembler Language
-----------------------------

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - id
        - int
        - The ID of the assembler language.

    *   - provider_ID
        - int
        - The ID of the provider that supports this language.

    *   - supported_language
        - str (enum)
        - The AssemblerLanguage (Enum) which is supported.

=====

Quantum Program
-----------------

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - id
        - int
        - The ID of the quantum program.

    *   - quantum_circuit
        - str
        - Quantum code that will be executed.

    *   - assembler_language
        - str
        - Assembler language in which the code should be interpreted.

    *   - deployment_id
        - int
        - The deployment where a list of quantum program is used.

    *   - python_file_path
        - str
        - Part of experimental feature: path to file to be uploaded (to IBM)

    *   - python_file_metadata
        - str
        - Part of experimental feature: metadata for the python_file

    *   - python_file_options
        - str
        - Part of experimental feature: options for the python_file

    *   - python_file_inputs
        - str
        - Part of experimental feature: inputs for the python_file

=====

Result
-----------------

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - id
        - int
        - The ID of the result.

    *   - result_dict
        - dict
        - The results of the job, in the given result_type.
          For the Runner it should have the keys counts and probabilities.
          The counts and probabilities should be a dict with hexadecimals as quantum-bit-keys.

    *   - job_id
        - int
        - The job_id that was executed.

    *   - circuit
        - int
        - The circuit which was executed by the job.

    *   - meta_data
        - int
        - Other data that was provided by the provider.

    *   - result_type
        - enum
        - Result type depending on the Job_Type of the job.

=====


