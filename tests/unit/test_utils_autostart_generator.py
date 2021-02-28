import pytest

from bigxml.utils import autostart_generator


@autostart_generator
def multiply(multiplier):
    value = yield
    while True:
        value = yield value * multiplier


def test_valid():
    generator = multiply(6)
    assert generator.send(2) == 12
    assert generator.send(7) == 42


@autostart_generator
def yes():
    while True:
        yield "y"


def test_invalid():
    with pytest.raises(ValueError):
        yes()
