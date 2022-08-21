from typing import Callable, Iterator, Union
from unittest.mock import Mock

import pytest

from bigxml.handle_mgr import HandleMgr
from bigxml.nodes import XMLElement, XMLText


def handler_a(_node: Union[XMLElement, XMLText]) -> Iterator[int]:
    yield 13
    yield 37


def handler_b(_node: Union[XMLElement, XMLText]) -> Iterator[int]:
    yield 42


def handler_c(_node: Union[XMLElement, XMLText]) -> Iterator[object]:
    yield from ()


def handle(
    handler: Callable[[Union[XMLElement, XMLText]], Iterator[int]]
) -> Iterator[int]:
    node = Mock()
    for item in handler(node):
        yield item * 1_000


def test_iter_from_no_handle() -> None:
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.iter_from(handler_a)


def test_return_from_no_handle() -> None:
    hmgr = HandleMgr()
    with pytest.raises(RuntimeError):
        hmgr.return_from(handler_a)


def test_iter_from_handle() -> None:
    hmgr = HandleMgr()
    hmgr._handle = handle  # pylint: disable=protected-access
    assert list(hmgr.iter_from(handler_a)) == [13_000, 37_000]
    assert list(hmgr.iter_from(handler_b)) == [42_000]
    assert not list(hmgr.iter_from(handler_c))


def test_return_from_handle() -> None:
    hmgr = HandleMgr()
    hmgr._handle = handle  # pylint: disable=protected-access
    assert hmgr.return_from(handler_a) == 37_000
    assert hmgr.return_from(handler_b) == 42_000
    assert hmgr.return_from(handler_c) is None
