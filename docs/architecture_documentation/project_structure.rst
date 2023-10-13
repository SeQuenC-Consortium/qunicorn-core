Project Structure
#####################

This chapter gives a brief overview of the project structure of the qunicorn project.
Describing the different packages and components within.
The Structure described can be found within the qunicorn_core folder.

Structure of the project
*************************



api <Package>:
^^^^^^^^^^^^^^^^

The api package contains all the api views and models. It is used to define the API.

* api_models <Package>:
    * DTOS and Schemas for all Objects
    * these are used for computation and to define the schemas for the api views
* deployment_api <Package>:
    * contains the api definition for deployments.
* device_api <Package>:
    * contains the api definition for devices.
* job_api <Package>:
    * contains the api definition for jobs.
* provider_api <Package>:
    * contains the api definition for providers.
* user_api <Package>:
    * contains the api definition for users.

core <Package>:
^^^^^^^^^^^^^^^^

The core package contains all the core logic of the project. This includes mappers and various services.

* mapper <Package>:
    * Contains mappers to map between different objects.
    * this includes:
        * mapping from DTOs to Dataclass objects
        * mapping from Schemas to DTOs
* pilotmanager <Package>:
    * This package contains the different pilots, which are used to communicate with different quantum providers
    * Includes the pilot_manager, a service class for handling of pilot data.
    * pilot_resources <Package>:
        * Contains resources for the pilots in the json format.
* transpiler <Package>:
    * Includes the transpiler, which is used to transpile between assembler languages used by different providers.
* deployment_service <.py File>
    * A service file for deployments which handles communication between the api and other parts of the core package and the db package.
* device_service <.py File>
    * A service file for devices which handles communication between the api and other parts of the core package and the db package.
* job_manager_service <.py File>
     * A service file to prepare jobs for execution on one of the pilots.
* job_service <.py File>
    * A service file for jobs which handles communication between the api and other parts of the core package and the db package.
* provider_service <.py File>
    * A service file for providers which handles communication between the api and other parts of the core package and the db package.
* user_service <.py File>
    * IS EMPTY

db <Package>:
^^^^^^^^^^^^^^^^

The db package contains the database models and the database service. It is used to define the database, and to handle communication with it.

* database_services <Package>:
   * Holds services which provide access the database (add, get, update, remove).
   * Services are called from the core package.
* models <Package>:
    * Holds the definitions of the various database models.
* cli <.py File>:
    * Contains cli commands to interact with the database, such as setting up the database or pushing clean data.
* db <.py File>:
    * Holds DB constant to avoid circular imports.

static <Package>:
^^^^^^^^^^^^^^^^^^

The static package contains all static files, such as the enums used in the qunicorn project.

* enums <Package>:
    * contains all enums used within the project.

util <Package>:
^^^^^^^^^^^^^^^^

The util package contains various util files, as well as config files for the project.

* config <Package>:
    * Contains config files for the project.
    * These include: Celery, Smorest and sqlalchemy config files.
* debug_routes <Package>:
    * Contains routes for debugging purposes.
* logging <.py File>:
    * Util file to set up logging.
* reserve_proxy_fix <.py File>
    * Util file to set up reverse proxy fix.
* utils <.py File>:
    * Util file to set up general util methods.
