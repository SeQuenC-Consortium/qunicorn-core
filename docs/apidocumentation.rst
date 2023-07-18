API Documentation
=================

Generated Documentation
-----------------------

Below you can find a generated Documentation of the API. 

* `Api documentation <api.html>`_

=====

Structure Overview
------------------

This is how the structure of the API looks like.

* api-root 
    * GET /
* jobmanager-api
    * GET       /jobs/                              [List all jobs]                 ->  Code: 200
    * POST      /jobs/                              [Create a new job]              ->  Code: 201
    * GET       /jobs/{job_id}/                     [Get a job]                     ->  Code: 200
    * DELETE    /jobs/{job_id}/                     [Delete a job]                  ->  Code: 200
    * POST      /jobs/run/{job_id}/                 [Run a job]                     ->  Code: 200
    * POST      /jobs/cancel/{job_id}/              [Cancel a job]                  ->  Code: 200
    * POST      /jobs/pause/{job_id}/               [Pause a job]                   ->  Code: 200
* devices-api
    * GET       /devices/                           [List all devices]              ->  Code: 200
    * GET       /devices/{device_id}/               [Get a device]                  ->  Code: 200
    * GET       /devices/{device_id}/status         [Get a device status]           ->  Code: 200
    * GET       /devices/{device_id}/calibration    [Get a device calibration]      ->  Code: 200
    * GET       /devices/{device_id}/jobs           [Get a device jobs]             ->  Code: 200
* deployment-api
    * GET       /deployments/                       [Get all deployments]          ->  Code: 200
    * POST      /deployments/                       [Create a new deployment]       ->  Code: 201
    * GET       /deployments/{deployment_id}/       [Get a deployment]              ->  Code: 200
    * PUT       /deployments/{deployment_id}/       [Update a deployment]           ->  Code: 200
    * PATCH     /deployments/{deployment_id}/       [Partially update a deployment] ->  Code: 200
    * DELETE    /deployments/{deployment_id}/       [Delete a deployment]           ->  Code: 200
    * GET       /deployments/{deployment_id}/jobs   [Get a deployment jobs]         ->  Code: 200
* services-api
    * GET       /provider/                          [List all providers]            ->  Code: 200
    * GET       /provider/{provider_id}/            [Get a provider]                ->  Code: 200
* users-api
    * GET       /users/                             [List all users]                ->  Code: 200
    * GET       /users/{user_id}/                   [Get a user]                    ->  Code: 200
