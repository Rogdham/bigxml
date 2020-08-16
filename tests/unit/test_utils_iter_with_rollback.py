import pytest

from bigxml.utils import IterWithRollback


def test_no_rollback():
    i = IterWithRollback("abcd")
    assert list(i) == ["a", "b", "c", "d"]


def test_rollback_start():
    i = IterWithRollback("abcd")
    i.rollback()
    assert list(i) == ["a", "b", "c", "d"]


def test_rollback():
    i = IterWithRollback("abcd")
    assert next(i) == "a"
    i.rollback()
    assert next(i) == "a"
    assert next(i) == "b"
    assert next(i) == "c"
    i.rollback()
    assert next(i) == "c"
    i.rollback()
    assert next(i) == "c"
    i.rollback()
    assert next(i) == "c"
    assert next(i) == "d"
    with pytest.raises(StopIteration):
        next(i)


def test_rollback_called_twice():
    i = IterWithRollback("abcd")
    assert next(i) == "a"
    assert next(i) == "b"
    i.rollback()
    i.rollback()
    assert next(i) == "b"
    assert next(i) == "c"
    assert next(i) == "d"
    with pytest.raises(StopIteration):
        next(i)
