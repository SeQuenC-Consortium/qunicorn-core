Project structure
#####################

Structure of the project
*************************

api:
* api_models package: DTOs and Schemas for all Objects
   * these are used for computation and to define the schemas for the api views
* {object}_api packages:
   * these include the definition of the different views

core:
* mapper package:
   * this includes different mappers from DTOs to Database Objects. A Helper class.
* {object}manager packages:
   * Computational classes: exist for different objects
   * Service classes: get called from api
       * All calls from API should be forwarded to these classes.
       * Celery tasks

db:
* database_services package:
   * services to access the database (add, get, update, remove)
* models package:
    * definition of various database models
