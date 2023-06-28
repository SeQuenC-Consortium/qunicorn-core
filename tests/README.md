# Pytest Testing
## How to run tests
Run pytest in poetry
> poetry run pytest tests/automated_tests

OR:

Install pytest
> pip install -U pytest

Execute tests by executing.
> pytest tests/automated_tests

Pytest finds test methods through the "test_" prefix.

## Mocking Methods
### Example:
> mocker.patch("qunicorn_core.core.pilotmanager.qiskit_pilot.QiskitPilot._QiskitPilot__get_ibm_provider", return_value=backend_mock)

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
