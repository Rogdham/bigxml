import pytest

from bigxml.utils import IterWithRollback


def test_no_rollback():
    i = IterWithRollback("abcd")
    assert i.iteration == 0
    assert list(i) == ["a", "b", "c", "d"]
    assert i.iteration == 4


def test_rollback_start():
    i = IterWithRollback("abcd")
    assert i.iteration == 0
    i.rollback()
    assert i.iteration == 0
    assert list(i) == ["a", "b", "c", "d"]
    assert i.iteration == 4


def test_rollback():
    i = IterWithRollback("abcd")
    assert i.iteration == 0
    assert next(i) == "a"
    assert i.iteration == 1
    i.rollback()
    assert i.iteration == 0
    assert next(i) == "a"
    assert i.iteration == 1
    assert next(i) == "b"
    assert i.iteration == 2
    assert next(i) == "c"
    assert i.iteration == 3
    i.rollback()
    assert i.iteration == 2
    assert next(i) == "c"
    assert i.iteration == 3
    i.rollback()
    assert i.iteration == 2
    assert next(i) == "c"
    assert i.iteration == 3
    i.rollback()
    assert i.iteration == 2
    assert next(i) == "c"
    assert i.iteration == 3
    assert next(i) == "d"
    assert i.iteration == 4
    with pytest.raises(StopIteration):
        next(i)
    assert i.iteration == 4


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
