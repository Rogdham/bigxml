from functools import partial
from unittest.mock import Mock

import pytest

from bigxml.handler_creator import create_handler
from bigxml.handler_marker import xml_handle_element, xml_handle_text
from bigxml.nodes import XMLElement, XMLElementAttributes, XMLText


def create_nodes(*path):
    # create nodes
    nodes = []
    for node_name in path:
        if node_name == ":text:":
            node = XMLText(text="text", parents=tuple(nodes))
        else:
            node = XMLElement(
                name=node_name,
                attributes=XMLElementAttributes({}),
                parents=tuple(nodes),
            )
        nodes.append(node)

    # set handles
    for i, parent in enumerate(nodes):
        if not isinstance(parent, XMLElement):
            continue
        try:
            child = nodes[i + 1]
            parent.set_handle(lambda h, child=child: h(child))
        except IndexError:
            parent.set_handle(lambda h: ())

    return nodes


def cases(*args):
    tests = []
    for node_path, expected_text, expected_node_name in args:
        nodes = create_nodes(*node_path)
        if expected_node_name is None:
            assert expected_text is None
            expected_node = None
        else:
            expected_node = nodes[node_path.index(expected_node_name)]

        def test_create_handler(root, expected_text, expected_node, *handles):
            handler = create_handler(*handles)
            out = list(handler(root))
            if expected_node is None:
                assert out == []
            else:
                assert out == [(expected_text, expected_node)]

        tests.append(
            pytest.param(
                partial(test_create_handler, nodes[0], expected_text, expected_node),
                id=">".join(node_path),
            )
        )

    return pytest.mark.parametrize("test_create_handler", tests)


#
# no handler
#


def test_no_handlers():
    handler = create_handler()
    node = Mock()
    assert list(handler(node)) == []


#
# function
#


@cases(
    (("a",), "catchall", "a"),
    (("{foo}a",), "catchall", "{foo}a"),
    (("d0", "d1"), "catchall", "d0"),
    (("d0", "d1", "d2"), "catchall", "d0"),
    ((":text:",), "catchall", ":text:"),
)
def test_one_catchall(test_create_handler):
    def catchall(node):
        yield ("catchall", node)

    test_create_handler(catchall)


@cases(
    (("a",), "0", "a"),
    (("{foo}a",), "1", "{foo}a"),
    (("{bar}a",), "0", "{bar}a"),
    (("b",), "2", "b"),
    (("c",), "2", "c"),
    (("d0",), None, None),
    (("d0", ":text:"), None, None),
    (("d0", "d1"), "3", "d1"),
    (("d0", "d1", "d2"), "3", "d1"),
    (("z",), None, None),
    ((":text:",), "4", ":text:"),
    ((":text:", "t"), "4", ":text:"),
    (("t0", "t1", ":text:"), "5", ":text:"),
    (("t0", "t1", ":text:", "t2"), "5", ":text:"),
)
def test_several_functions(test_create_handler):
    @xml_handle_element("a")
    def handle0(node):
        yield ("0", node)

    @xml_handle_element("{foo}a")
    def handle1(node):
        yield ("1", node)

    @xml_handle_element("b")
    @xml_handle_element("c")
    def handle2(node):
        yield ("2", node)

    @xml_handle_element("d0", "d1")
    def handle3(node):
        yield ("3", node)

    @xml_handle_text()
    def handle4(node):
        yield ("4", node)

    @xml_handle_text("t0", "t1")
    def handle5(node):
        yield ("5", node)

    test_create_handler(handle0, handle1, handle2, handle3, handle4, handle5)


@cases(
    (("a", ":text:", "b"), None, None),
)
def test_invalid_handle(test_create_handler):
    @xml_handle_element("a", XMLText.name, "b")
    def handle_invalid(node):
        yield ("nope", node)

    # just make sure it does not crash
    test_create_handler(handle_invalid)


#
# class instance
#


@cases(
    (("a",), "0", "a"),
    (("{foo}a",), "1", "{foo}a"),
    (("{bar}a",), "0", "{bar}a"),
    (("b",), "2", "b"),
    (("c",), "2", "c"),
    (("d0",), None, None),
    (("d0", ":text:"), None, None),
    (("d0", "d1"), "3", "d1"),
    (("d0", "d1", "d2"), "3", "d1"),
    (("z",), None, None),
    ((":text:",), "4", ":text:"),
    ((":text:", "t"), "4", ":text:"),
    (("t0", "t1", ":text:"), "5", ":text:"),
    (("t0", "t1", ":text:", "t2"), "5", ":text:"),
)
def test_class_instance(test_create_handler):
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node):
            yield ("0", node)

        @xml_handle_element("{foo}a")
        @staticmethod
        def handle1(node):
            yield ("1", node)

        @xml_handle_element("b")
        @xml_handle_element("c")
        @staticmethod
        def handle2(node):
            yield ("2", node)

        @xml_handle_element("d0", "d1")
        @staticmethod
        def handle3(node):
            yield ("3", node)

        @xml_handle_text()
        @staticmethod
        def handle4(node):
            yield ("4", node)

        @xml_handle_text("t0", "t1")
        @staticmethod
        def handle5(node):
            yield ("5", node)

    test_create_handler(Handler())


@cases(
    (("a",), None, None),
    (("x0", "a"), None, None),
    (("x0", "y0", "a"), "0", "a"),
    (("x0", "y0", "z", "a"), None, None),
    (("x1", "y1", "z", "a"), "0", "a"),
    (("x1", "y1", "z", "w", "a"), None, None),
)
def test_marked_class_instance(test_create_handler):
    @xml_handle_element("x0", "y0")
    @xml_handle_element("x1", "y1", "z")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node):
            yield ("0", node)

    test_create_handler(Handler())


@cases(
    (("a",), None, None),
    (("x",), None, None),
    (("x", "a"), None, None),
    (("x", "y0"), None, None),
    (("x", "y0", "a"), "0", "a"),
    (("x", "y0", "z"), None, None),
    (("x", "y0", "z", "a"), None, None),
    (("x", "y1"), None, None),
    (("x", "y1", "a"), "1", "a"),
    (("x", "y1", "z"), None, None),
    (("x", "y1", "z", "a"), None, None),
)
def test_deep_marked_class_instances(test_create_handler):
    @xml_handle_element("y0")
    class DeepHandler0:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node):
            yield ("0", node)

    @xml_handle_element("y1")
    class DeepHandler1:
        @xml_handle_element("a")
        @staticmethod
        def handle1(node):
            yield ("1", node)

    @xml_handle_element("x")
    class Handler:
        deep_handler0 = DeepHandler0()

        def __init__(self):
            self.deep_handler1 = DeepHandler1()

    test_create_handler(Handler())


#
# Invalid handler
#


def test_catchall_handler_not_alone():
    @xml_handle_element("a")
    def handle(node):
        yield ("0", node)

    def catchall(node):
        yield ("1", node)

    with pytest.raises(TypeError):
        create_handler(handle, catchall)


def test_several_catchall_handlers():
    def catchall0(node):
        yield ("0", node)

    def catchall1(node):
        yield ("1", node)

    with pytest.raises(TypeError):
        create_handler(catchall0, catchall1)


@pytest.mark.parametrize(
    "handler",
    (
        None,
        True,
        False,
        42,
        b"a",
        "a",
        ("a", "b"),
        ["a", "b"],
        {"a", "b"},
        {"a": lambda _: None},
        object,
        object(),
    ),
    ids=type,
)
def test_invalid_handler_type(handler):
    with pytest.raises(TypeError):
        create_handler(handler)
