from unittest.mock import Mock
import pytest

from bigxml.handle_mgr import HandleMgr


def test_no_handle():
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.iter_from(0)


def test_handle():
    hmgr = HandleMgr()

    handle = Mock()
    hmgr.set_handle(handle)
    handle.assert_not_called()

    hmgr.iter_from(0)
    handle.assert_called_once_with(0)

    with pytest.raises(RuntimeError):
        hmgr.iter_from(1)
    handle.assert_called_once()
