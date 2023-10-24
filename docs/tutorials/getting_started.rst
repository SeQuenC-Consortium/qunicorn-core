Getting started
=====================


This package uses `Poetry <https://python-poetry.org/docs//>`_.

VSCode
################

For vscode install the python extension and add the poetry venv path to the folders the python extension searches for
venvs.

On linux:

.. code-block:: bash

    json
    {
        "python.venvFolders": [
        "~/.cache/pypoetry/virtualenvs"
        ]
    }

Development
################

Run `poetry install` to install dependencies.

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
For this first download the forest-sdk on https://qcs.rigetti.com/sdk-downloads and then run the following commands:

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
Settings can be changed in the .flaskenv.

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
