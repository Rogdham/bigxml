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
    handle.return_value = iter((13, 37))
    hmgr.set_handle(handle)
    handle.assert_not_called()

    assert list(hmgr.iter_from(0)) == [13, 37]
    handle.assert_called_once_with(0)

    with pytest.raises(RuntimeError):
        hmgr.iter_from(1)
    handle.assert_called_once()


def test_return_from_no_handle():
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.return_from(0)


def test_return_from_handle():
    hmgr = HandleMgr()

    handle = Mock()
    handle.return_value = iter(())
    hmgr.set_handle(handle)
    handle.assert_not_called()

    assert hmgr.return_from(0) == 0
    handle.assert_called_once_with(0)

    with pytest.raises(RuntimeError):
        hmgr.return_from(1)
    handle.assert_called_once()


def test_return_from_handle_warns():
    hmgr = HandleMgr()

    handle = Mock()
    handle.return_value = iter((13, 37))
    hmgr.set_handle(handle)
    handle.assert_not_called()

    with pytest.warns(RuntimeWarning):
        assert hmgr.return_from(0) == 0
    handle.assert_called_once_with(0)

    with pytest.raises(RuntimeError):
        hmgr.return_from(1)
    handle.assert_called_once()
