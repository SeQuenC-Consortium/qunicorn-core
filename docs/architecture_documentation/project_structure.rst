Project Structure
#####################

This site gives a brief overview of the project structure of the qunicorn project.
Describing the different packages and components within.

The Structure described can be found within the **qunicorn_core** package.

Structure of the project
*************************

api <Package>:
^^^^^^^^^^^^^^^^

The api package contains all the api views and models. It is used to define the API.

* api_models <Package>:
    * Contains DTOS and Schemas for all Objects
    * These are used for computation and to define the schemas for the api views
* {component}_api <Package>:
    * Contains the api definition for a component.

core <Package>:
^^^^^^^^^^^^^^^^

The core package contains all the core logic of the project. This includes mappers and various services.

* mapper <Package>:
    * Contains mappers to map between different objects.
    * This includes:
        * mapping from DTOs to Dataclass objects
        * mapping from Schemas to DTOs
* pilotmanager <Package>:
    * Contains the different pilots, which are used to communicate with different quantum providers
    * Contains the pilot_manager, a service class for handling of pilot data.
    * pilot_resources <Package>:
        * Contains resources for the pilots in the json format.
* transpiler <Package>:
    * Contains the transpiler, which is used to transpile between assembler languages used by different providers.
* {component}_service <.py File>
    * A service file for a component which handles communication between the api and other parts of the core package and the db package.

db <Package>:
^^^^^^^^^^^^^^^^

The db package contains the database models and the database service. It is used to define the database, and to handle communication with it.

* models <Package>:
    * Contains the definitions of the various database models.
* cli <.py File>:
    * Contains cli commands to interact with the database, such as setting up the database or pushing clean data.
* db <.py File>:
    * Contains DB constant to avoid circular imports.

static <Package>:
^^^^^^^^^^^^^^^^^^

The static package contains all static files, such as the enums used in the qunicorn project.

* enums <Package>:
    * Contains all enums used within the project.

util <Package>:
^^^^^^^^^^^^^^^^

The util package contains various util files, as well as config files for the project.

* config <Package>:
    * Contains config files for the project.
    * These include: Celery, Smorest and SQLAlchemy config files.
* debug_routes <Package>:
    * Contains routes for debugging purposes.
* logging <.py File>:
    * A util file to set up logging.
* reserve_proxy_fix <.py File>
    * A util file to set up reverse proxy fix.
* utils <.py File>:
    * A util file to set up general util methods.
