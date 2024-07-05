Workflows and Pytest
=====================

Workflows:
##########

* Configured in :file:`.github/workflows`
* Formatting-linting.yml
    * Executes linting provided by flake8 and black, configured in :file:`.flake8`
* run-pytests.yml
    * Executed tests defined in :file:`/tests/automated_tests/`

PyTest
#########

* General Documentation: `pytest Documentation <https://docs.pytest.org/en/8.2.x/>`_
* Tests can be found in :file:`/tests`
* Install pytest with

.. code-block:: bash

    pip install -U pytest

* Executed in Terminal with

.. code-block:: bash

    pytest tests/automated_tests/

* pytest finds test methods through the ``test_``  prefix

Test Structure
###############
Structure of a test execution should follow  `Given-When-Then <https://pythontest.com/strategy/given-when-then-2/>`_


Test Environment
#################

Make sure to set the Environment, some methods need to be called with app_context:

.. code-block:: bash

    with app.app_context()

Notes:
********

* Sometimes the DB is not updated when within the same app_context block, try creating another block and call from there.
* Mocks do not work within async celery task, due to it running on an external broker.

Further documentation can be found in the `pytest documentation <https://docs.pytest.org/en/7.1.x/getting-started.html>`_ .

