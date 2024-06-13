Getting started
=====================


This package uses `Poetry <https://python-poetry.org/docs//>`_.

VSCode
################

For VSCode, install the python extension and add the poetry venv path to the folders the python extension searches for
venvs.

On linux:

.. code-block:: bash

    json
    {
        "python.venvFolders": [
        "~/.cache/pypoetry/virtualenvs"
        ]
    }

Pycharm
################

For Pycharm, there is a detailed guide in the documentation: :doc:`Pycharm Docu - Development Guide <./configure_pycharm>`.
Including some hints on how to develop qunicorn.

Development
################

Run :code:`poetry install` to install dependencies.

Environment variables
#########################

The flask dev server loads environment variables from `.flaskenv` and `.env`.
To override any variable create a `.env` file.
Environment variables in `.env` take precedence over `.flaskenv`.
See the content of the `.flaskenv` file for the default environment variables.

You can also add an `IBM_TOKEN` to the `.env` file to use the IBM backend without a token in each request.
Set the `EXECUTE_CELERY_TASK_ASYNCHRONOUS` in your .env file to False, if you don't want to start a
celery worker and execute all tasks synchronously.
Set the `ENABLE_EXPERIMENTAL_FEATURES` in your .env file to True, if you want to use experimental features like
the qasm to quil transpilation, and IBM File_Runner and File_Upload job types.

Run the Development Server
###########################

Run the development server with

.. code-block:: bash

   poetry run flask run


Start Docker, init the celery worker and then start it

.. code-block:: bash

   poetry run invoke start-broker
   poetry run invoke worker


Create the initial database (If this doesn't work, try to delete the db-file from the "instance" folder)

.. code-block:: bash

   flask create-and-load-db


If you want to run requests using the rigetti pilot you need to have instances of quilc and qvm running.
For this, first download the forest-sdk on https://qcs.rigetti.com/sdk-downloads and then run the following commands:

.. code-block:: bash

    // Terminal 1

    quilc -S

    // Terminal 2

    qvm -S

Check Linting Errors

.. code-block:: bash

   poetry run invoke check-linting

Userful Links
#####################

Trying out the Template
************************

For a list of all dependencies with their license open http://localhost:5005/licenses.
The Port for qunicorn_core is set to 5005 to not interfere with other flask default apps.
Settings can be changed in the :file:`.flaskenv`.

The API:
**********************

http://localhost:5005/

OpenAPI Documentation:
**********************

Configured in `qunicorn_core/util/config/smorest_config.py`.

* Redoc (view only): http://localhost:5005/redoc
* Rapidoc: http://localhost:5005/rapidoc
* Swagger-UI: http://localhost:5005/swagger-ui
* OpenAPI Spec (JSON): http://localhost:5005/api-spec.json

Debug pages:
**********************

* Index: http://localhost:5005/debug/
* Registered Routes: http://localhost:5005/debug/routes | Useful for looking up which endpoint is served under a route or what routes are available.



How to check if the pipeline will succeed
-----------------------------------------

1. :code:`poetry run invoke check-linting`

    a. If black fails fix it with: :code:`poetry run black .`

    b. If flake8 fails fix it with: :code:`poetry run flake8`

2. :code:`poetry run pytest ./tests/automated_tests/`


How to test the user authentication
-----------------------------------

Checkout the Keycloak documentation :doc:`here <../architecture_documentation/authentication>`.


How to write documentation
--------------------------

Use Read the docs for that: :doc:`ReadTheDocs - Setup and Testing <./rtd_setup_testing>`


Other useful commands
----------------------

To add some flask or invoke commands see :doc:`Useful Commands <./useful_commands>` in the documentation.
