from functools import partial
from unittest.mock import Mock

import pytest

from bigxml.handler_creator import CLASS_HANDLER_METHOD_NAME, create_handler
from bigxml.handler_marker import xml_handle_element, xml_handle_text
from bigxml.nodes import XMLElement, XMLElementAttributes, XMLText


def create_nodes(*path, parent=None):
    # create nodes
    nodes = [parent] if parent is not None else []
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
    for i, node_parent in enumerate(nodes):
        if not isinstance(node_parent, XMLElement):
            continue

        # get existing children
        try:
            children = list(node_parent.iter_from(lambda n: (n,)))
        except RuntimeError:
            children = []

        # append new children
        try:
            children.append(nodes[i + 1])
        except IndexError:
            pass

        # create handle
        def handle(handler, _children):
            for child in _children:
                yield from handler(child)

        # pylint: disable=protected-access
        node_parent._handle = lambda h, c=children: handle(h, c)

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
            elif expected_text is None:
                assert out == [expected_node]
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
# syntactic_sugar
#


@cases(
    (("a",), None, "a"),
    (("{foo}a",), None, "{foo}a"),
    (("b",), None, None),
    (("b", "a"), None, None),
)
@pytest.mark.parametrize(
    "handler",
    ("a", ("a",), ["a"]),
    ids=type,
)
def test_syntactic_sugar_one_level(test_create_handler, handler):
    test_create_handler(handler)


@cases(
    (("a",), None, None),
    (("a", "b"), None, "b"),
    (("{foo}a", "b"), None, "b"),
    (("a", "{bar}b"), None, "{bar}b"),
    (("{foo}a", "{bar}b"), None, "{bar}b"),
    (("b",), None, None),
    (("c", "a", "b"), None, None),
)
@pytest.mark.parametrize(
    "handler",
    (("a", "b"), ["a", "b"]),
    ids=type,
)
def test_syntactic_sugar_two_levels(test_create_handler, handler):
    test_create_handler(handler)


#
# class instance & class (generic case)
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
@pytest.mark.parametrize("instantiate_class", (False, True))
def test_class_instance(test_create_handler, instantiate_class):
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

    handler = Handler() if instantiate_class else Handler
    test_create_handler(handler)


@cases(
    (("a",), None, None),
    (("x0", "a"), None, None),
    (("x0", "y0", "a"), "0", "a"),
    (("x0", "y0", "z", "a"), None, None),
    (("x1", "y1", "z", "a"), "0", "a"),
    (("x1", "y1", "z", "w", "a"), None, None),
)
@pytest.mark.parametrize("instantiate_class", (False, True))
def test_marked_class_instance(test_create_handler, instantiate_class):
    @xml_handle_element("x0", "y0")
    @xml_handle_element("x1", "y1", "z")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node):
            yield ("0", node)

    handler = Handler() if instantiate_class else Handler
    test_create_handler(handler)


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
@pytest.mark.parametrize("instantiate_class", (False, True))
def test_deep_marked_class_instances(test_create_handler, instantiate_class):
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

    handler = Handler() if instantiate_class else Handler
    test_create_handler(handler)


#
# class instance
#


@cases(
    (("x", "a"), "0", "a"),
)
def test_class_instance_with_handler(test_create_handler):
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node):
            yield ("0", node)

        def xml_handler(self):
            raise RuntimeError(self)  # testing that it is not called

    handler = Handler()
    assert hasattr(handler, CLASS_HANDLER_METHOD_NAME)
    test_create_handler(handler)


#
# class
#


def test_class_init():
    @xml_handle_element("x", "y")
    class Handler:
        init_nb = 0

        def __init__(self, node):
            self.init_nb = Handler.init_nb
            Handler.init_nb += 1
            self.root = node
            self.seen_nodes = 0

        @xml_handle_element("a", "b")
        def handle0(self, node):
            yield (self.init_nb, self.root, self.seen_nodes, node)
            self.seen_nodes += 1

    #   x -> y0 -> a0 -> b0
    #                 -> b1
    #           -> a1 -> b2
    #     -> y1 -> a2 -> b3
    #
    # Handler should be instanciated on y0 and y1
    #
    # the use of namespaces below is to avoid e.g. node_y0==node_y1
    #
    # pylint: disable=unbalanced-tuple-unpacking
    node_x, node_y0 = create_nodes("x", "{y0}y")
    _, node_a0, node_b0 = create_nodes("{a0}a", "{b0}b", parent=node_y0)
    _, node_b1 = create_nodes("{b1}b", parent=node_a0)
    _, _, node_b2 = create_nodes("{a1}a", "{b2}b", parent=node_y0)
    _, node_y1, _, node_b3 = create_nodes("{n1}y", "{a2}a", "{b3}b", parent=node_x)
    # pylint: enable=unbalanced-tuple-unpacking

    handler = create_handler(Handler)
    assert list(handler(node_x)) == [
        (0, node_y0, 0, node_b0),
        (0, node_y0, 1, node_b1),
        (0, node_y0, 2, node_b2),
        (1, node_y1, 0, node_b3),
    ]
    assert Handler.init_nb == 2


def test_class_init_no_mandatory_parameters():
    @xml_handle_element("x")
    class Handler:
        def __init__(self, answer=42):
            self.answer = answer

        @xml_handle_element("a")
        def handle0(self, node):
            yield ("0", self.answer, node)

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    assert list(handler(nodes[0])) == [("0", 42, nodes[1])]


def test_class_init_one_mandatory_parameter():
    @xml_handle_element("x")
    class Handler:
        def __init__(self, node, answer=42):
            self.node = node
            self.answer = answer

        @xml_handle_element("a")
        def handle0(self, node):
            yield ("0", self.node, self.answer, node)

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    assert list(handler(nodes[0])) == [("0", nodes[0], 42, nodes[1])]


def test_class_init_two_mandatory_parameters():
    @xml_handle_element("x")
    class Handler:
        def __init__(self, node, answer):
            self.node = node
            self.answer = answer

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.raises(TypeError) as excinfo:
        list(handler(nodes[0]))

    assert "__init__ should have" in str(excinfo.value)
    assert "node, answer" in str(excinfo.value)


def test_class_init_crash():
    @xml_handle_element("x")
    class Handler:
        def __init__(self):
            raise TypeError("Something went wrong")

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.raises(TypeError) as excinfo:
        list(handler(nodes[0]))

    assert str(excinfo.value) == "Something went wrong"


def test_class_with_handler():
    @xml_handle_element("x")
    class Handler:
        def __init__(self):
            self.nodes = []

        @xml_handle_element("a")
        def handle0(self, node):
            self.nodes.append(("x", node))

        @xml_handle_element("b")
        def handle1(self, node):
            self.nodes.append(("y", node))

        def xml_handler(self):
            yield ("start", None)
            for txt, node in self.nodes:
                yield ("_{}".format(txt), node)
            yield ("end", None)

    # pylint: disable=unbalanced-tuple-unpacking
    node_x, node_a = create_nodes("x", "a")
    _, node_b = create_nodes("b", parent=node_x)
    # pylint: enable=unbalanced-tuple-unpacking

    handler = create_handler(Handler)
    assert list(handler(node_x)) == [
        ("start", None),
        ("_x", node_a),
        ("_y", node_b),
        ("end", None),
    ]


def test_class_with_handler_static_method():
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node):
            yield ("0", node)  # this creates a warning

        @staticmethod
        def xml_handler():
            yield ("end", None)

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.warns(RuntimeWarning):
        assert list(handler(nodes[0])) == [("end", None)]


def test_class_with_handler_generator():
    @xml_handle_element("x")
    class Handler:
        def __init__(self):
            self.nodes = []

        @xml_handle_element("a")
        def handle0(self, node):
            self.nodes.append(("x", node))
            yield ("0", node)

        @xml_handle_element("b")
        def handle1(self, node):
            self.nodes.append(("y", node))
            yield ("1", node)

        def xml_handler(self, generator):
            yield ("start", None)
            for txt, node in self.nodes:
                # before consuming the generator, self.nodes is empty
                # the following line is never run
                yield ("oops{}".format(txt), node)
            for txt, node in generator:
                yield ("h{}".format(txt), node)
            for txt, node in self.nodes:
                yield ("_{}".format(txt), node)
            yield ("end", None)

    # pylint: disable=unbalanced-tuple-unpacking
    node_x, node_a = create_nodes("x", "a")
    _, node_b = create_nodes("b", parent=node_x)
    # pylint: enable=unbalanced-tuple-unpacking

    handler = create_handler(Handler)
    assert list(handler(node_x)) == [
        ("start", None),
        ("h0", node_a),
        ("h1", node_b),
        ("_x", node_a),
        ("_y", node_b),
        ("end", None),
    ]


def test_class_with_handler_static_method_generator():
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node):
            yield ("0", node)

        @xml_handle_element("b")
        @staticmethod
        def handle1(node):
            yield ("1", node)

        @staticmethod
        def xml_handler(generator):
            yield ("start", None)
            for txt, node in generator:
                yield ("h{}".format(txt), node)
            yield ("end", None)

    # pylint: disable=unbalanced-tuple-unpacking
    node_x, node_a = create_nodes("x", "a")
    _, node_b = create_nodes("b", parent=node_x)
    # pylint: enable=unbalanced-tuple-unpacking

    handler = create_handler(Handler)
    assert list(handler(node_x)) == [
        ("start", None),
        ("h0", node_a),
        ("h1", node_b),
        ("end", None),
    ]


def test_class_with_handler_too_many_mandatory_params():
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node):
            yield ("0", node)

        @staticmethod
        def xml_handler(generator, extra):
            for item in generator:
                yield (extra, item)

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.raises(TypeError) as excinfo:
        list(handler(nodes[0]))

    assert "xml_handler should have" in str(excinfo.value)
    assert "generator, extra" in str(excinfo.value)


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
        {"a", "b"},
        {"a": lambda _: None},
        object(),
    ),
    ids=type,
)
def test_invalid_handler_type(handler):
    with pytest.raises(TypeError):
        create_handler(handler)
