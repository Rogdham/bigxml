import pytest

from bigxml.utils import last_item_or_none


@pytest.mark.parametrize(
    "iterable, expected",
    (
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
    ),
    ids=repr,
)
def test_last_item_or_none(iterable, expected):
    assert last_item_or_none(iterable) == expected
