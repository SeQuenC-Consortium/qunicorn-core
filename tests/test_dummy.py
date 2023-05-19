import pytest


def function_to_test(x, y):
    return x + y


def f():
    raise SystemExit(1)


# First Test Dummy, expects 2
def test_function():
    assert function_to_test(1, 1) == 2


# Second Test Dummy, expects SystemExit
def test_f():
    with pytest.raises(SystemExit):
        f()
