# Pytest Testing

## General

Our tests are split in two different folders.
First the automated tests and second the manual tests.
Currently only synchronous flows are tested, because its more reliable and efficient.

### Automated Tests

These tests from "tests/automated_tests" are run during the git pipeline.
They should not test any connection to a Quantum Computer Provider.
Each method in this directory that starts with "test_" will be executed.

### Manual Tests

These test can be manually triggered to the App End-To-End with also the Quantum Computer Providers.
They are found in "tests/manual_tests".
To test the IBM Runner/Sampler or Estimator, a token need to be added to the Environment Variables.
The key should be "IBM_TOKEN" and the token can be copied from your landing page at https://quantum-computing.ibm.com/.
Instead, the token could also be added to the "job_request_dto_test_data.json"-File.

## How to run tests

Run pytest in poetry
> poetry run pytest tests/automated_tests

OR: Install pytest
> pip install -U pytest

Execute tests by executing.
> pytest tests/automated_tests

Pytest finds test methods through the "test_" prefix.

## Test Structure

Structure of a test execution should follow https://pythontest.com/strategy/given-when-then-2/

## Mocking Methods

### Example:

> mocker.patch("qunicorn_core.core.pilotmanager.qiskit_pilot.QiskitPilot._QiskitPilot__get_ibm_provider",
> return_value=backend_mock)

> mocker.patch("qunicorn_core.core.pilotmanager.qiskit_pilot.QiskitPilot.transpile", return_value=(backend_mock, None))

Note:

* Calling private Method Through: Object.\_Object__private_method_
* return_value sets the return Value

### Using Mocking Objects:

Create Mock through:
> mock = Mock()

Mock a method with a return value:
> mock.method_name.return_value = value

## Environment

Make sure to set the Environment, some methods need to be called with app_context:
> with app.app_context()

Notes:

* Sometimes DB is not updated when within the same app_context block, try creating another and calling from there.
* Mocks do not work within async celery task, due to it running on external broker.

Further documentation can be found in the [pytest documentation](https://docs.pytest.org/en/7.1.x/getting-started.html).
