from unittest.mock import Mock

import pytest

from bigxml.handle_mgr import HandleMgr


def handler_a(_node):
    yield 13
    yield 37


def handler_b(_node):
    yield 42


def handler_c(_node):
    yield from ()


def handle(handler):
    node = Mock()
    for item in handler(node):
        yield f"<{item}>"


def test_iter_from_no_handle():
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.iter_from(handler_a)


def test_return_from_no_handle():
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.return_from(handler_a)


def test_iter_from_handle():
    hmgr = HandleMgr()
    hmgr._handle = handle  # pylint: disable=protected-access
    assert list(hmgr.iter_from(handler_a)) == ["<13>", "<37>"]
    assert list(hmgr.iter_from(handler_b)) == ["<42>"]
    assert list(hmgr.iter_from(handler_c)) == []


def test_return_from_handle():
    hmgr = HandleMgr()
    hmgr._handle = handle  # pylint: disable=protected-access
    assert hmgr.return_from(handler_a) == "<37>"
    assert hmgr.return_from(handler_b) == "<42>"
    assert hmgr.return_from(handler_c) is None
