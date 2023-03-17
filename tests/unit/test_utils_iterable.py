from typing import Iterable

import pytest

from bigxml.utils import consume, last_item_or_none


@pytest.mark.parametrize(
    ["iterable", "expected"],
    [
        # no items
        ((), None),
        (iter(()), None),
        ("", None),
        # one item
        (("hello",), "hello"),
        (iter(("world",)), "world"),
        ("a", "a"),
        # several items
        ("abcd", "d"),
        (range(43), 42),
    ],
    ids=repr,
)
def test_last_item_or_none(iterable: Iterable[object], expected: object) -> None:
    assert last_item_or_none(iterable) == expected


def test_consume() -> None:
    iterator = iter("abc")
    assert consume(iterator) is True
    with pytest.raises(StopIteration):
        next(iterator)


@pytest.mark.parametrize(
    ["iterable", "expected"],
    [
        # no items
        ((), False),
        (iter(()), False),
        ("", False),
        # one item
        (("hello",), True),
        (iter(("world",)), True),
        ("a", True),
        # several items
        ("abcd", True),
        (range(43), True),
    ],
    ids=repr,
)
def test_consume_return_value(iterable: Iterable[object], expected: object) -> None:
    assert consume(iterable) is expected
