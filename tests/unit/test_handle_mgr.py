from unittest.mock import Mock
import pytest

from bigxml.handle_mgr import HandleMgr


def test_no_handle():
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.handle(0)


def test_handle():
    hmgr = HandleMgr()

    handle = Mock()
    hmgr.set_handle(handle)
    handle.assert_not_called()

    hmgr.handle(0)
    handle.assert_called_once_with(0)

    with pytest.raises(RuntimeError):
        hmgr.handle(1)
    handle.assert_called_once()
