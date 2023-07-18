Database Models
=====

Deployments
-------

Attributes of Deployment Data

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - deployment_id 
        - int 
        - Automatically generated database id. Use the id to fetch this information from the database.

    *   - deployment_name 
        - str (optional) 
        - Optional name for a deployment
        
    *   - user_id 
        - str 
        - A user_id associated to the deployment
        
    *   - created 
        - Date 
        - Date of the creation of a deployment

    *   - parameters 
        - str 
        - The parameters for the Job. Job parameters should already be prepared and error checked before starting the task.

    *   - data 
        - Union[dict, list, str, float, int, bool, None] 
        - Mutable JSON-like store for additional lightweight task data. Default value is empty dict.
   
=====

Jobs
-------

Attributes of Job Data

..  list-table::
    :header-rows: 1
    :widths: 20 20 60

    *   - Attribute
        - Type
        - Description

    *   - job_id 
        - int 
        - Automatically generated database id. Use the id to fetch this information from the database.

    *   - job_name 
        - str (optional) 
        - Optional name for a job

    *   - user_id 
        - str 
        - A user_id associated to the job

    *   - deployment_id 
        - int 
        - A deployment_id associated with the job

    *   - started_at 
        - datetime (optional) 
        - The moment the job was scheduled. (default :py:func:`~datetime.datetime.utcnow`)

    *   - finished_at 
        - Optional[datetime] (optional) 
        - The moment the job finished successfully or with an error.

    *   - parameters 
        - str 
        - The parameters for the Job. Job parameters should already be prepared and error checked before starting the task.

    *   - data 
        - Union[dict, list, str, float, int, bool, None] 
        - Mutable JSON-like store for additional lightweight task data. Default value is empty dict.

    *   - task_status 
        - Optional[str] (optional) 
        - The status of a job, can only be ``PENDING``, ``RUNNING`` ,``FINISHED``, or ``ERROR``.

    *   - results 
        - List[Job] (optional) 
        - The output data (files) of the job
   
