from unittest.mock import Mock

import pytest

import bigxml.handler as module
from bigxml.handler import XMLHandler, xml_handle_element, xml_handle_text
from bigxml.nodes import XMLText

# pragma pylint: disable=protected-access


@pytest.fixture
def join_handlers(monkeypatch):
    mock = Mock()
    mock.return_value = mock._handler
    mock._handler.return_value = (13, 37)
    monkeypatch.setattr(module, "join_handlers", mock)
    yield mock


# pragma pylint: disable=redefined-outer-name


def test_no_handlers(join_handlers):
    handler = XMLHandler()
    node = Mock()
    assert list(handler(node)) == [13, 37]
    join_handlers.assert_called_once()
    jh_args, jh_kwargs = join_handlers.call_args
    assert len(jh_args) == 1
    assert not jh_kwargs
    assert list(jh_args[0]) == []
    join_handlers._handler.assert_called_once_with(node)


def test_many_handlers(join_handlers):
    class Handler(XMLHandler):
        # pylint: disable=no-self-use

        @xml_handle_element("a", "b")
        def handle_x(self, node):
            yield ("x", node)

        @xml_handle_text("c")
        def handle_y(self, node):
            yield ("y", node)

        @xml_handle_element("d", "e")
        @xml_handle_text("f")
        @xml_handle_element("g")
        def handle_z(self, node):
            yield ("z", node)

    handler = Handler()
    node = Mock()
    assert list(handler(node)) == [13, 37]
    join_handlers.assert_called_once()
    jh_args, jh_kwargs = join_handlers.call_args
    assert len(jh_args) == 1
    assert not jh_kwargs
    assert set(jh_args[0]) == {
        (("a", "b"), handler.handle_x),
        (("c", XMLText.name), handler.handle_y),
        (("d", "e"), handler.handle_z),
        (("f", XMLText.name), handler.handle_z),
        (("g",), handler.handle_z),
    }
    join_handlers._handler.assert_called_once_with(node)
