# The Qunicorn Core - Unification Middleware for a sovereign Quantum Cloud

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Python: >= 3.8](https://img.shields.io/badge/python-^3.8-blue)
[![Formatting and linting](https://github.com/SeQuenC-Consortium/qunicorn-core/actions/workflows/formatting-linting.yml/badge.svg)](https://github.com/SeQuenC-Consortium/qunicorn-core/actions/workflows/formatting-linting.yml)
[![Runs python tests](https://github.com/SeQuenC-Consortium/qunicorn-core/actions/workflows/run-pytests.yml/badge.svg)](https://github.com/SeQuenC-Consortium/qunicorn-core/actions/workflows/run-pytests.yml)

This package uses Poetry ([documentation](https://python-poetry.org/docs/)).

## VSCode

For vscode install the python extension and add the poetry venv path to the folders the python extension searches for
venvs.

On linux:

```json
{
  "python.venvFolders": [
    "~/.cache/pypoetry/virtualenvs"
  ]
}
```

## Development

Run `poetry install` to install dependencies.

The flask dev server loads environment variables from `.flaskenv` and `.env`.
To override any variable create a `.env` file.
Environment variables in `.env` take precedence over `.flaskenv`.
See the content of the `.flaskenv` file for the default environment variables.

The currently available endpoints are:
* **POST /jobs/** *(Create/Register and run new job)*
  * Needs a valid token to connect to IBM
  * Runs asynchronously so the results are not shown in the api response  
* **GET /jobs/{job_id}/** *(Get details/results of a job)*

Run the development server with

```bash
poetry run flask run
```

Start Docker, init the celery worker and then start it

```bash
poetry run invoke start-broker
poetry run invoke worker
```

Create the initial database

```bash
flask create-and-load-db
```

Check Linting Errors

```bash
poetry run invoke check-linting
```

### Trying out the Template

For a list of all dependencies with their license open <http://localhost:5005/licenses/>.
The Port for qunicorn_core is set to 5005 to not interfere with other flask default apps.
Settings can be changed in the .flaskenv.

#### The API:

<http://localhost:5005/>

#### OpenAPI Documentation:

Configured in `qunicorn_core/util/config/smorest_config.py`.

* Redoc (view only): <http://localhost:5005/redoc>
* Rapidoc: <http://localhost:5005/rapidoc>
* Swagger-UI: <http://localhost:5005/swagger-ui>
* OpenAPI Spec (JSON): <http://localhost:5005/api-spec.json>

#### Debug pages:

* Index: <http://localhost:5005/debug/>
* Registered Routes: <http://localhost:5005/debug/routes>\
  Useful for looking up which endpoint is served under a route or what routes are available.

#### Remarks

For more detailed information about additional commands see the readme.md in docs.

## Disclaimer of Warranty

Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its
Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including,
without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the Work
and assume any risks associated with Your exercise of permissions under this License.

## Haftungsausschluss

Dies ist ein Forschungsprototyp. Die Haftung für entgangenen Gewinn, Produktionsausfall, Betriebsunterbrechung,
entgangene Nutzungen, Verlust von Daten und Informationen, Finanzierungsaufwendungen sowie sonstige Vermögens- und
Folgeschäden ist, außer in Fällen von grober Fahrlässigkeit, Vorsatz und Personenschäden, ausgeschlossen.

## Acknowledgements

The initial code contribution has been supported by the
project [SeQuenC](https://www.iaas.uni-stuttgart.de/forschung/projekte/sequenc/).
