import pytest

from bigxml.marks import add_mark, get_marks, has_marks


@pytest.mark.parametrize("instantiate", [True, False])
def test_marks(instantiate: bool) -> None:
    class Markable:
        pass

    obj = Markable() if instantiate else Markable

    assert not has_marks(obj)
    assert not get_marks(obj)

    add_mark(obj, ("abc",))
    assert has_marks(obj)
    assert get_marks(obj) == (("abc",),)

    add_mark(obj, ("def", "ghi", "jkl"))
    assert has_marks(obj)
    assert get_marks(obj) == (("abc",), ("def", "ghi", "jkl"))
