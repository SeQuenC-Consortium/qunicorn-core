API Documentation
=================

Generated Documentation
-----------------------

Below you can find a generated Documentation of the API. 

* `Api documentation <../../api.html>`_

Examples for the request bodies for job and deployment creation can be found in the repository `here <https://github.com/qunicorn/qunicorn-core/tree/main/tests/test_resources>`_

For deployment or job creation, the required information can be retrieved from the other api endpoints. e.g. the names of the devices defined by the provider (GET /devices/) to create a new job (POST /jobs/)

=====

Available Endpoints
--------------------

Available endpoints are:

* **JOBS**
    * **GET /jobs/** *(Get all jobs)*
    * **POST /jobs/** *(Create/Register and run new job)*
        * Needs a valid token to connect to IBM, local simulations from AWS or Rigetti work without a token
        * Runs asynchronously so the results are not shown in the api response
    * **GET /jobs/{job_id}/** *(Get details/results of a job)*
    * **DELETE /jobs/{job_id}/** *(Delete a job and return Deleted Job Details)*
    * **POST /jobs/run/{job_id}/** *(Executes an uploaded python file)*
    * **POST /jobs/rerun/{job_id}/** *(Copies and Runs again an existing Job)*
    * **POST /jobs/cancel/{job_id}/** *(Cancel a job that has be started)*

* **DEVICES**
    * **GET /devices/** *(Get all currently saved devices)*
    * **PUT /devices/** *(Updates the device list from the provider)*
    * **GET /devices/{device_id}/** *(Get details about one device)*
    * **POST /devices/{device_id}/status** *(To check if a device is available)*
    * **POST /devices/{device_id}/calibration** *(To get device properties for configuration)*

* **DEPLOYMENTS**
    * **GET /deployments/** *(Get all Deployments)*
    * **POST /deployments/** *(Create a Deployment)*
    * **GET /deployments/{deployment_id}/** *(Get a Deployment by ID)*
    * **PUT /deployments/{deployment_id}/** *(Update a Deployment)*
    * **DELETE /deployments/{deployment_id}/** *(Deletes a Deployment)*
    * **GET /deployments/{deployment_id}/jobs** *(Get the details of all jobs with a specific deployment id)*
    * **DELETE /deployments/{deployment_id}/jobs** *(Delete all jobs with a specific deployment id)*

* **PROVIDER**
    * **GET /provider/** *(Get all providers from the database)*
    * **GET /provider/{provider_id}/** *(Get details of a provider)*
