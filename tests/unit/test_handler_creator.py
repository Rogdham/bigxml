from unittest.mock import Mock

import pytest

from bigxml.handler_creator import handler_from_dict, join_handlers
from bigxml.nodes import XMLElement, XMLText


@pytest.fixture
def nodes():
    all_nodes = ()
    for name in "abc":
        node = XMLElement(name, {}, all_nodes)
        all_nodes += (node,)

    def set_handle(node, child=None):
        handle = Mock()
        if child is None:
            handle.side_effect = NotImplementedError  # should not happen
        else:
            handle.side_effect = lambda h: h(child)
        node.set_handle(handle)
        node.test_handle = handle

    set_handle(all_nodes[0], all_nodes[1])
    set_handle(all_nodes[1], all_nodes[2])
    set_handle(all_nodes[2])

    yield all_nodes


# pragma pylint: disable=redefined-outer-name


def test_handler_from_dict_miss_direct(nodes):
    handle = handler_from_dict({})
    assert list(handle(nodes[0])) == []
    nodes[0].test_handle.assert_not_called()
    nodes[1].test_handle.assert_not_called()
    nodes[2].test_handle.assert_not_called()


def test_handler_from_dict_miss_deep(nodes):
    handle = handler_from_dict({"a": {"b": {}}})
    assert list(handle(nodes[0])) == []
    nodes[0].test_handle.assert_called_once()
    nodes[1].test_handle.assert_called_once()
    nodes[2].test_handle.assert_not_called()


def test_handler_from_dict_direct(nodes):
    handler = Mock()
    handler.return_value = (13, 37)
    handle = handler_from_dict({"a": handler})
    assert list(handle(nodes[0])) == [13, 37]
    nodes[0].test_handle.assert_not_called()
    nodes[1].test_handle.assert_not_called()
    nodes[2].test_handle.assert_not_called()
    handler.assert_called_once_with(nodes[0])


def test_handler_from_dict_deep(nodes):
    handler = Mock()
    handler.return_value = (13, 37)
    handle = handler_from_dict({"a": {"b": {"c": handler}}})
    assert list(handle(nodes[0])) == [13, 37]
    nodes[0].test_handle.assert_called_once()
    nodes[1].test_handle.assert_called_once()
    nodes[2].test_handle.assert_not_called()
    handler.assert_called_once_with(nodes[2])


def test_handler_from_dict_text_invalid_handler(nodes):
    text_node = XMLText("Hello", (nodes[0],))
    nodes[0].test_handle.side_effect = lambda h: h(text_node)
    handle = handler_from_dict({"a": {XMLText.name: {}}})
    assert list(handle(nodes[0])) == []
    nodes[0].test_handle.assert_called_once()
    nodes[1].test_handle.assert_not_called()
    nodes[2].test_handle.assert_not_called()


@pytest.mark.parametrize(
    "name, expected",
    (
        ("{}aaa", [0]),
        ("{xxx}aaa", [0]),
        ("{yyy}aaa", [0]),
        ("{}bbb", []),
        ("{xxx}bbb", [1]),
        ("{yyy}bbb", []),
        ("{}ccc", [3]),
        ("{xxx}ccc", [2]),
        ("{yyy}ccc", [2]),
        ("{}ddd", [4]),
        ("{xxx}ddd", [5]),
        ("{yyy}ddd", [4]),
        ("{}eee", [7]),
        ("{xxx}eee", [6]),
        ("{yyy}eee", [7]),
    ),
)
def test_handler_from_dict_namespace(name, expected):
    handle = handler_from_dict(
        {
            "aaa": lambda _: (0,),
            "{xxx}bbb": lambda _: (1,),
            "ccc": lambda _: (2,),
            "{}ccc": lambda _: (3,),
            # different path in code depending on order of key without namespace
            "ddd": lambda _: (4,),
            "{xxx}ddd": lambda _: (5,),
            "{xxx}eee": lambda _: (6,),
            "eee": lambda _: (7,),
        }
    )
    node = XMLElement(name, {}, ())
    assert list(handle(node)) == expected


def test_join_handlers(nodes):
    handler = Mock()
    handler.return_value = (13, 37)

    def handlers():
        yield (("a", "b", "c"), handler)

    handle = join_handlers(handlers())
    assert list(handle(nodes[0])) == [13, 37]
    nodes[0].test_handle.assert_called_once()
    nodes[1].test_handle.assert_called_once()
    nodes[2].test_handle.assert_not_called()
    handler.assert_called_once_with(nodes[2])
