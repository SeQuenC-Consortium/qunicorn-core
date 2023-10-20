UseCases
========

To demo/show and test the application with UseCases, the WorkflowModeler is needed.
The WorkflowModeler is a web application that can be used to create and edit workflows.
It can be found in the following repository: https://github.com/PlanQK/workflow-modeler

To create a UseCase you can start the Docker Compose from the UseCase repository:
https://github.com/SeQuenC-Consortium/SeQuenC-UseCases/

The following services should now be available under:
- qunicorn: localhost:5005/swagger-ui/
- workflow-modeler: localhost:8080/
- camunda: localhost:8078/camunda/app/

To create a new UseCase check the README of the UseCase repository.

Example UseCase: Get Devices and Create Job
-------------------------------------------

1. Get all devices
2. UserTask: Let the user evaluate the results, the user can now select a device
3. Create a job with the chosen device, and other user inputs
4. Get the results/details of the job
5. UserTask: Let the user evaluate the results

    .. image:: ../resources/images/use_case_1_bpmn.JPG
