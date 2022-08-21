import pytest

from bigxml.utils import IterWithRollback


def test_no_rollback() -> None:
    i = IterWithRollback("abcd")
    assert i.iteration == 0
    assert list(i) == ["a", "b", "c", "d"]
    assert i.iteration == 4


def test_rollback_start() -> None:
    i = IterWithRollback("abcd")
    assert i.iteration == 0
    i.rollback()
    assert i.iteration == 0
    assert list(i) == ["a", "b", "c", "d"]
    assert i.iteration == 4


def test_rollback() -> None:
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


def test_rollback_called_twice() -> None:
    i = IterWithRollback("abcd")
    assert i.iteration == 0
    assert next(i) == "a"
    assert i.iteration == 1
    assert next(i) == "b"
    assert i.iteration == 2
    i.rollback()
    assert i.iteration == 1
    i.rollback()
    assert i.iteration == 1
    assert next(i) == "b"
    assert i.iteration == 2
    assert next(i) == "c"
    assert i.iteration == 3
    assert next(i) == "d"
    assert i.iteration == 4
    with pytest.raises(StopIteration):
        next(i)
