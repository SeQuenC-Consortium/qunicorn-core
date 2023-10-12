API Documentation
=================

Generated Documentation
-----------------------

Below you can find a generated Documentation of the API. 

* `Api documentation <api.html>`_

=====

Available Endpoints
--------------------

Available endpoints are:

* **JOBS**
    * **POST /jobs/** *(Create/Register and run new job)*
        * Needs a valid token to connect to IBM
        * Runs asynchronously so the results are not shown in the api response
    * **GET /jobs/** *(Get all jobs)*
    * **GET /jobs/{job_id}/** *(Get details/results of a job)*
    * **DELETE /jobs/{job_id}/** *(Get details/results of a job)*
    * **POST /jobs/run/{job_id}/** *(Executes an uploaded python file)*
    * **POST /jobs/rerun/{job_id}/** *(Copies and Runs again an existing Job)*
    * **GET /jobs/{deployment_id}/** *(Get all jobs with the given deploymentId)*
    * **DELETE /jobs/{deployment_id}/** *(Delete all jobs with the given deploymentId)*

* **DEPLOYMENTS**
    * **GET /deployments/** *(Get all Deployments)*
    * **POST /deployments/** *(Create a Deployment)*
    * **GET /deployments/{deployment_id}/** *(Gets a Deployment)*
    * **PUT /deployments/{deployment_id}/** *(Update a Deployment)*
    * **DELETE /deployments/{deployment_id}/** *(Deletes a Deployment)*

* **DEVICES**
    * **GET /devices/** *(Get all currently saved devices)*
    * **PUT /devices/** *(Updates the devices, by retrieving them from IBM)*
    * **PUT /devices/{device_id}/** *(Get details about one device)*
    * **PUT /devices/{device_id}/status** *(To check if a device is running)*
    * **PUT /devices/{device_id}/calibration** *(To get some device properties)*
