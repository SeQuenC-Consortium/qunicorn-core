Linting and Formatting
=======================

Local Linting with Flake8 (VSC):
################################

* Install Flake8 Extension
* If python environment included flake8 already, it will automatically start linting the python files
    * Otherwise: Install Flake8 (Flake8: Your Tool For Style Guide Enforcement — flake8 6.1.0 documentation )
* Qunicorn Flake8 Settings can be found in .flake8
* Display the current problems in the console: “flake8 .”
* Check for Linting Errors  (black & flake) with:

.. code-block:: bash

    poetry run invoke check-linting

Flake8 Settings
****************

* Ignore singular line:

.. code-block:: bash

    # noqa

at end of line

* Ignore whole file:

.. code-block:: bash

    # flake8: noqa

At start of file

* Ignore certain warnings in files, add to .flake8 file

.. code-block:: bash

    per-file-ignores =
        filename:ErrorCode

    e.g.:

    per-file-ignores =
        __init__.py:F401,F403,C901

Formatting with black
################################

* Install Black

.. code-block:: bash

    pip install black

* Check if there are open black warnings/errors in the project

.. code-block:: bash

    black --check .

* Run Black on File:

.. code-block:: bash

    black filename

* OR: Run Black on directory or directly on the current navigated folder

.. code-block:: bash

    black directory
    black .

    This will automatically format the selected files

* Files or directories can also be excluded

.. code-block:: bash

    black --check --extend-exclude="regex" directory

* To get more information on the progress add --verbose option

Automatic Formatting on Save
*****************************

* In Pycharm:
    * Strg+Alt+A → Search for “Actions on Save” → check “Reformat code” and “Optimize imports”
    * “Settings” → “Editor” → “Code Style” → “Python”
    * Furthermore: Disable Line breaks reformatting and increase hard wrap
