from contextlib import suppress
from dataclasses import dataclass
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)
from unittest.mock import Mock

import pytest

from bigxml.handler_creator import CLASS_HANDLER_METHOD_NAME, create_handler
from bigxml.handler_marker import xml_handle_element, xml_handle_text
from bigxml.nodes import XMLElement, XMLElementAttributes, XMLText

if TYPE_CHECKING:
    # see https://github.com/pytest-dev/pytest/issues/7469
    # for pytest exporting from pytest and not _pytest
    from _pytest.mark import ParameterSet


def create_nodes(
    *path: str, parent: Optional[Union[XMLElement, XMLText]] = None
) -> List[Union[XMLElement, XMLText]]:
    # create nodes
    nodes = [parent] if parent is not None else []
    for node_name in path:
        # the cast below is wrong but makes our life easier
        # plus that case is kind of tested in tests below
        parents = tuple(cast(List[XMLElement], nodes))
        if node_name == ":text:":
            node: Union[XMLElement, XMLText] = XMLText(text="text", parents=parents)
        else:
            node = XMLElement(
                name=node_name,
                attributes=XMLElementAttributes({}),
                parents=parents,
            )
        nodes.append(node)

    # set handles
    for i, node_parent in enumerate(nodes):
        if not isinstance(node_parent, XMLElement):
            continue

        # get existing children
        try:
            children: List[Union[XMLElement, XMLText]] = list(
                node_parent.iter_from(lambda n: (n,))
            )
        except RuntimeError:
            children = []

        # append new children
        with suppress(IndexError):
            children.append(nodes[i + 1])

        # create handle
        def handle(
            handler: Callable[[Union[XMLElement, XMLText]], Iterator[object]],
            children: List[Union[XMLElement, XMLText]],
        ) -> Iterable[object]:
            for child in children:
                yield from handler(child)

        # pylint: disable=protected-access
        node_parent._handle = partial(handle, children=children)  # type: ignore[assignment]

    return nodes


def cases(
    *args: Tuple[Tuple[str, ...], Optional[str], Optional[str]]
) -> pytest.MarkDecorator:
    tests: List["ParameterSet"] = []
    for node_path, expected_text, expected_node_name in args:
        nodes = create_nodes(*node_path)
        if expected_node_name is None:
            assert expected_text is None
            expected_node = None
        else:
            expected_node = nodes[node_path.index(expected_node_name)]

        def test_create_handler(
            root: Union[XMLElement, XMLText],
            expected_text: Optional[str],
            expected_node: Optional[str],
            *handles: object,
        ) -> None:
            handler = create_handler(*handles)
            out = list(handler(root))
            if expected_node is None:
                assert not out
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


TEST_CREATE_HANDLER_TYPE = Callable[..., None]  # pylint: disable=invalid-name

#
# no handler
#


def test_no_handlers() -> None:
    handler = create_handler()
    node = Mock()
    assert not list(handler(node))


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
def test_one_catchall(test_create_handler: TEST_CREATE_HANDLER_TYPE) -> None:
    def catchall(
        node: Union[XMLElement, XMLText]
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
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
def test_several_functions(test_create_handler: TEST_CREATE_HANDLER_TYPE) -> None:
    @xml_handle_element("a")
    def handle0(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
        yield ("0", node)

    @xml_handle_element("{foo}a")
    def handle1(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
        yield ("1", node)

    @xml_handle_element("b")
    @xml_handle_element("c")
    def handle2(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
        yield ("2", node)

    @xml_handle_element("d0", "d1")
    def handle3(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
        yield ("3", node)

    @xml_handle_text()
    def handle4(node: XMLText) -> Iterator[Tuple[str, XMLText]]:
        yield ("4", node)

    @xml_handle_text("t0", "t1")
    def handle5(node: XMLText) -> Iterator[Tuple[str, XMLText]]:
        yield ("5", node)

    test_create_handler(handle0, handle1, handle2, handle3, handle4, handle5)


@cases(
    (("a", ":text:", "b"), None, None),
)
def test_invalid_handle(test_create_handler: TEST_CREATE_HANDLER_TYPE) -> None:
    @xml_handle_element("a", XMLText.name, "b")
    def handle_invalid(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
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
    ["a", ("a",), ["a"]],
    ids=type,
)
def test_syntactic_sugar_one_level(
    test_create_handler: TEST_CREATE_HANDLER_TYPE, handler: object
) -> None:
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
    [("a", "b"), ["a", "b"]],
    ids=type,
)
def test_syntactic_sugar_two_levels(
    test_create_handler: TEST_CREATE_HANDLER_TYPE, handler: object
) -> None:
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
@pytest.mark.parametrize("instantiate_class", [False, True])
def test_class_instance(
    test_create_handler: TEST_CREATE_HANDLER_TYPE, instantiate_class: bool
) -> None:
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("0", node)

        @xml_handle_element("{foo}a")
        @staticmethod
        def handle1(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("1", node)

        @xml_handle_element("b")
        @xml_handle_element("c")
        @staticmethod
        def handle2(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("2", node)

        @xml_handle_element("d0", "d1")
        @staticmethod
        def handle3(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("3", node)

        @xml_handle_text()
        @staticmethod
        def handle4(node: XMLText) -> Iterator[Tuple[str, XMLText]]:
            yield ("4", node)

        @xml_handle_text("t0", "t1")
        @staticmethod
        def handle5(node: XMLText) -> Iterator[Tuple[str, XMLText]]:
            yield ("5", node)

        @staticmethod
        def xml_handler(
            generator: Iterator[Tuple[str, Union[XMLElement, XMLText]]]
        ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
            yield from generator

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
@pytest.mark.parametrize("instantiate_class", [False, True])
def test_marked_class_instance(
    test_create_handler: TEST_CREATE_HANDLER_TYPE, instantiate_class: bool
) -> None:
    @xml_handle_element("x0", "y0")
    @xml_handle_element("x1", "y1", "z")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("0", node)

        @staticmethod
        def xml_handler(
            generator: Iterator[Tuple[str, XMLElement]]
        ) -> Iterator[Tuple[str, XMLElement]]:
            yield from generator

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
@pytest.mark.parametrize("instantiate_class", [False, True])
def test_deep_marked_class_instances(
    test_create_handler: TEST_CREATE_HANDLER_TYPE, instantiate_class: bool
) -> None:
    @xml_handle_element("y0")
    class DeepHandler0:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("0", node)

        @staticmethod
        def xml_handler(
            generator: Iterator[Tuple[str, XMLElement]]
        ) -> Iterator[Tuple[str, XMLElement]]:
            yield from generator

    @xml_handle_element("y1")
    class DeepHandler1:
        @xml_handle_element("a")
        @staticmethod
        def handle1(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("1", node)

        @staticmethod
        def xml_handler(
            generator: Iterator[Tuple[str, XMLElement]]
        ) -> Iterator[Tuple[str, XMLElement]]:
            yield from generator

    @xml_handle_element("x")
    class Handler:
        deep_handler0 = DeepHandler0()

        def __init__(self) -> None:
            self.deep_handler1 = DeepHandler1()

        @staticmethod
        def xml_handler(
            generator: Iterator[Tuple[str, XMLElement]]
        ) -> Iterator[Tuple[str, XMLElement]]:
            yield from generator

    handler = Handler() if instantiate_class else Handler
    test_create_handler(handler)


#
# class instance
#


@cases(
    (("x", "a"), "0", "a"),
)
def test_class_instance_with_handler(
    test_create_handler: TEST_CREATE_HANDLER_TYPE,
) -> None:
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("0", node)

        def xml_handler(self) -> Iterator[object]:
            raise RuntimeError(self)  # testing that it is not called

    handler = Handler()
    assert hasattr(handler, CLASS_HANDLER_METHOD_NAME)
    test_create_handler(handler)


#
# class
#


def test_class_without_sub_handler() -> None:
    @xml_handle_element("x")
    class Handler:
        pass

    nodes = create_nodes("x", "y")
    handler = create_handler(Handler)
    items = list(handler(nodes[0]))
    assert len(items) == 1
    assert isinstance(items[0], Handler)


@pytest.mark.parametrize("init_mandatory", [False, True])
@pytest.mark.parametrize("init_optional", [False, True])
def test_class_init(init_mandatory: bool, init_optional: bool) -> None:
    # pylint: disable=too-many-locals

    @xml_handle_element("x", "y")
    class HandlerA:
        def __init__(self, node: XMLElement, answer: int = 42) -> None:
            self.seen: List[XMLElement] = []
            self.root = node
            self.answer = answer

        @xml_handle_element("a", "b")
        def handle0(self, node: XMLElement) -> None:
            self.seen.append(node)

    @xml_handle_element("x", "y")
    class HandlerB:
        def __init__(self, node: XMLElement) -> None:
            self.seen: List[XMLElement] = []
            self.root = node

        @xml_handle_element("a", "b")
        def handle0(self, node: XMLElement) -> None:
            self.seen.append(node)

    @xml_handle_element("x", "y")
    class HandlerC:
        def __init__(self, answer: int = 42) -> None:
            self.seen: List[XMLElement] = []
            self.answer = answer

        @xml_handle_element("a", "b")
        def handle0(self, node: XMLElement) -> None:
            self.seen.append(node)

    @xml_handle_element("x", "y")
    class HandlerD:
        def __init__(self) -> None:
            self.seen: List[XMLElement] = []

        @xml_handle_element("a", "b")
        def handle0(self, node: XMLElement) -> None:
            self.seen.append(node)

    if init_mandatory:
        if init_optional:
            Handler: Type[object] = HandlerA  # noqa: N806
        else:
            Handler = HandlerB  # noqa: N806
    else:
        if init_optional:  # noqa: PLR5501
            Handler = HandlerC  # noqa: N806
        else:
            Handler = HandlerD  # noqa: N806

    #   x -> y0 -> a0 -> b0
    #                 -> b1
    #           -> a1 -> b2
    #     -> y1 -> a2 -> b3
    #
    # Handler should be instantiated on y0 and y1
    #
    # the use of namespaces below is to avoid e.g. node_y0==node_y1
    #
    # pylint: disable=unbalanced-tuple-unpacking
    node_x, node_y0 = create_nodes("x", "{y0}y")
    _, node_a0, node_b0 = create_nodes("{a0}a", "{b0}b", parent=node_y0)
    _, node_b1 = create_nodes("{b1}b", parent=node_a0)
    _, _, node_b2 = create_nodes("{a1}a", "{b2}b", parent=node_y0)
    _, node_y1, _, node_b3 = create_nodes("{y1}y", "{a2}a", "{b3}b", parent=node_x)
    # pylint: enable=unbalanced-tuple-unpacking

    handler = create_handler(Handler)
    items: List[Any] = list(handler(node_x))
    assert all(isinstance(item, Handler) for item in items)
    assert len(items) == 2
    assert items[0].seen == [node_b0, node_b1, node_b2]
    assert items[1].seen == [node_b3]
    if init_mandatory:
        assert items[0].root == node_y0
        assert items[1].root == node_y1
    if init_optional:
        assert items[0].answer == 42
        assert items[1].answer == 42


def test_class_init_text_node() -> None:
    @xml_handle_text("x", "y0")
    @xml_handle_element("x", "y1")
    class Handler:
        def __init__(self, node: XMLElement) -> None:
            self.root = node
            self.node: Optional[XMLText] = None

        @xml_handle_text
        def handle0(self, node: XMLText) -> None:
            self.node = node

    #   x -> y0 -> :text:
    #     -> y1 -> z
    # pylint: disable=unbalanced-tuple-unpacking
    node_x, _, node_txt0 = create_nodes("x", "y0", ":text:")
    _, node_y1, node_txt1 = create_nodes("y1", ":text:", parent=node_x)
    # pylint: enable=unbalanced-tuple-unpacking

    handler = create_handler(Handler)
    items: List[Any] = list(handler(node_x))
    assert all(isinstance(item, Handler) for item in items)
    assert len(items) == 2
    assert items[0].root == node_txt0
    assert items[0].node is None
    assert items[1].root == node_y1
    assert items[1].node == node_txt1


def test_class_init_two_mandatory_parameters() -> None:
    @xml_handle_element("x")
    class Handler:
        def __init__(self, node: XMLElement, answer: int) -> None:
            self.node = node
            self.answer = answer

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.raises(TypeError) as excinfo:
        list(handler(nodes[0]))

    assert "__init__ should have" in str(excinfo.value)
    assert "node, answer" in str(excinfo.value)
    assert "Add a default value for dataclass fields" not in str(excinfo.value)


def test_dataclass_init_two_mandatory_parameters() -> None:
    @xml_handle_element("x")
    @dataclass
    class Handler:
        node: XMLElement
        answer: int

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.raises(TypeError) as excinfo:
        list(handler(nodes[0]))

    assert "__init__ should have" in str(excinfo.value)
    assert "node, answer" in str(excinfo.value)
    assert "Add a default value for dataclass fields" in str(excinfo.value)


def test_class_init_crash() -> None:
    @xml_handle_element("x")
    class Handler:
        def __init__(self) -> None:
            raise TypeError("Something went wrong")

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.raises(TypeError) as excinfo:
        list(handler(nodes[0]))

    assert str(excinfo.value) == "Something went wrong"


def test_class_with_handler() -> None:
    @xml_handle_element("x")
    class Handler:
        def __init__(self) -> None:
            self.nodes: List[Tuple[str, XMLElement]] = []

        @xml_handle_element("a")
        def handle0(self, node: XMLElement) -> None:
            self.nodes.append(("x", node))

        @xml_handle_element("b")
        def handle1(self, node: XMLElement) -> None:
            self.nodes.append(("y", node))

        def xml_handler(self) -> Iterator[Tuple[str, Optional[XMLElement]]]:
            yield ("start", None)
            for txt, node in self.nodes:
                yield (f"_{txt}", node)
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


def test_class_no_handler_warning() -> None:
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node: XMLElement) -> Iterable[Tuple[str, XMLElement]]:
            yield ("0", node)  # this creates a warning

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.warns(UserWarning):
        items = list(handler(nodes[0]))
    assert len(items) == 1
    assert isinstance(items[0], Handler)


def test_class_with_handler_static_method() -> None:
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node: XMLElement) -> Iterable[Tuple[str, XMLElement]]:
            yield ("0", node)  # this creates a warning

        @staticmethod
        def xml_handler() -> Iterable[Tuple[str, None]]:
            yield ("end", None)

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.warns(UserWarning):
        assert list(handler(nodes[0])) == [("end", None)]


def test_class_with_handler_generator() -> None:
    @xml_handle_element("x")
    class Handler:
        def __init__(self) -> None:
            self.nodes: List[Tuple[str, XMLElement]] = []

        @xml_handle_element("a")
        def handle0(self, node: XMLElement) -> Iterable[Tuple[str, XMLElement]]:
            self.nodes.append(("x", node))
            yield ("0", node)

        @xml_handle_element("b")
        def handle1(self, node: XMLElement) -> Iterable[Tuple[str, XMLElement]]:
            self.nodes.append(("y", node))
            yield ("1", node)

        def xml_handler(
            self, generator: Iterable[Tuple[str, XMLElement]]
        ) -> Iterable[Tuple[str, Optional[XMLElement]]]:
            yield ("start", None)
            for txt, node in self.nodes:
                # before consuming the generator, self.nodes is empty
                # the following line is never run
                yield (f"oops{txt}", node)
            for txt, node in generator:
                yield (f"h{txt}", node)
            for txt, node in self.nodes:
                yield (f"_{txt}", node)
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


def test_class_with_handler_static_method_generator() -> None:
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node: XMLElement) -> Iterable[Tuple[str, XMLElement]]:
            yield ("0", node)

        @xml_handle_element("b")
        @staticmethod
        def handle1(node: XMLElement) -> Iterable[Tuple[str, XMLElement]]:
            yield ("1", node)

        @staticmethod
        def xml_handler(
            generator: Iterable[Tuple[str, XMLElement]]
        ) -> Iterable[Tuple[str, Optional[XMLElement]]]:
            yield ("start", None)
            for txt, node in generator:
                yield (f"h{txt}", node)
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


def test_class_with_handler_too_many_mandatory_params() -> None:
    @xml_handle_element("x")
    class Handler:
        @xml_handle_element("a")
        @staticmethod
        def handle0(node: XMLElement) -> Iterator[Tuple[str, XMLElement]]:
            yield ("0", node)

        @staticmethod
        def xml_handler(
            generator: Iterable[Tuple[str, XMLElement]], extra: int
        ) -> Iterator[Tuple[int, str, XMLElement]]:
            for item in generator:
                yield (extra, *item)

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.raises(TypeError) as excinfo:
        list(handler(nodes[0]))

    assert "xml_handler should have" in str(excinfo.value)
    assert "generator, extra" in str(excinfo.value)


def test_class_with_handler_invalid_returned_value() -> None:
    @xml_handle_element("x")
    class Handler:
        @staticmethod
        def xml_handler() -> int:
            return 42

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    with pytest.raises(TypeError) as excinfo:
        next(handler(nodes[0]))

    assert "xml_handler should have returned None or an iterable" in str(excinfo.value)


def test_class_extends_builtin_str_without_init() -> None:
    @xml_handle_element("x")
    class Handler(str):
        pass

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    assert list(handler(nodes[0])) == [""]


def test_class_extends_builtin_list_without_init() -> None:
    @xml_handle_element("x")
    class Handler(List[XMLElement]):
        @xml_handle_element("a")
        def handle0(self, node: XMLElement) -> None:
            self.append(node)

    nodes = create_nodes("x", "a")
    handler = create_handler(Handler)
    assert list(handler(nodes[0])) == [[nodes[1]]]


#
# Invalid handler
#


def test_catchall_handler_not_alone() -> None:
    @xml_handle_element("a")
    def handle(
        node: Union[XMLElement, XMLText]
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield ("0", node)

    def catchall(
        node: Union[XMLElement, XMLText]
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield ("1", node)

    # ok alone
    create_handler(handle)
    create_handler(catchall)

    # ko together
    with pytest.raises(TypeError) as exc_info:
        create_handler(handle, catchall)
    assert str(exc_info.value).startswith("(): handlers exist: {'a': ")
    with pytest.raises(TypeError) as exc_info:
        create_handler(catchall, handle)
    assert str(exc_info.value).startswith("(): catchall handler exists: <function ")


def test_several_catchall_handlers() -> None:
    def catchall0(
        node: Union[XMLElement, XMLText]
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield ("0", node)

    def catchall1(
        node: Union[XMLElement, XMLText]
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield ("1", node)

    with pytest.raises(TypeError) as exc_info:
        create_handler(catchall0, catchall1)
    assert str(exc_info.value).startswith("(): catchall handler exists: <function ")


def test_concurrent_handlers() -> None:
    @xml_handle_element("a", "b", "c")
    def handle0(
        node: Union[XMLElement, XMLText]
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield ("0", node)

    @xml_handle_element("a", "b", "c")
    def handle1(
        node: Union[XMLElement, XMLText]
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield ("0", node)

    with pytest.raises(TypeError) as exc_info:
        create_handler(handle0, handle1)
    assert str(exc_info.value).startswith(
        "('a', 'b', 'c'): catchall handler exists: <function "
    )


@pytest.mark.parametrize(
    "handler",
    [
        None,
        True,
        False,
        42,
        b"a",
        {"a", "b"},
        {"a": lambda _: None},
        object(),
    ],
    ids=type,
)
def test_invalid_handler_type(handler: object) -> None:
    with pytest.raises(TypeError):
        create_handler(handler)
