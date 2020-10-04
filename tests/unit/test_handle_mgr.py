from unittest.mock import Mock

import pytest

from bigxml.handle_mgr import HandleMgr


def test_iter_from_no_handle():
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.iter_from(0)


def test_iter_from_handle():
    hmgr = HandleMgr()

    handle = Mock()
    handle.side_effect = ((13, 37), (42,))
    hmgr.set_handle(handle)
    handle.assert_not_called()

    assert list(hmgr.iter_from(0)) == [13, 37]
    handle.assert_called_once_with(0)

    assert list(hmgr.iter_from(1)) == [42]
    handle.assert_called_with(1)


def test_return_from_no_handle():
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.return_from(0)


def test_return_from_handle():
    hmgr = HandleMgr()

    handle = Mock()
    handle.side_effect = ((13, 37), (42,), ())
    hmgr.set_handle(handle)
    handle.assert_not_called()

    assert hmgr.return_from(0) == 37
    handle.assert_called_once_with(0)

    assert hmgr.return_from(1) == 42
    handle.assert_called_with(1)

    assert hmgr.return_from(2) is None
    handle.assert_called_with(2)
