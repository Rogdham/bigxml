from typing import Generator

from bigxml.utils import autostart_generator


@autostart_generator
def multiply(multiplier: int) -> Generator[int, int, None]:
    value = yield -1  # ignored
    while True:
        value = yield value * multiplier


def test_valid() -> None:
    generator = multiply(6)
    assert generator.send(2) == 12
    assert generator.send(7) == 42


@autostart_generator
def count() -> Generator[int, None, None]:
    yield from range(100)


def test_ignore_first() -> None:
    generator = count()
    # 0 is skipped
    assert next(generator) == 1
