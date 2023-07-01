from functools import partial
from typing import Literal

import pytest

from bigxml.marks import add_mark, get_marks, has_marks


@pytest.mark.parametrize("case", ["class", "instance", "function", "partial"])
def test_marks(case: Literal["class", "instance", "function", "partial"]) -> None:
    class Markable:
        pass

    def markable(i: int, j: int) -> int:
        return i * j

    obj = {
        "class": Markable,
        "instance": Markable(),
        "function": markable,
        "partial": partial(markable, 42),
    }[case]

    assert not has_marks(obj)
    assert not get_marks(obj)

    add_mark(obj, ("abc",))
    assert has_marks(obj)
    assert get_marks(obj) == (("abc",),)

    add_mark(obj, ("def", "ghi", "jkl"))
    assert has_marks(obj)
    assert get_marks(obj) == (("abc",), ("def", "ghi", "jkl"))
