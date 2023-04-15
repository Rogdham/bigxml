from itertools import count
from typing import Callable, Dict, Iterator, List, Optional, Tuple, Union

import pytest

from bigxml.handler_marker import xml_handle_element
from bigxml.nodes import XMLElement, XMLElementAttributes, XMLText
from bigxml.parser import Parser

HANDLER_TYPE = Callable[  # pylint: disable=invalid-name
    [Union[XMLElement, XMLText]],
    Iterator[Tuple[str, Union[XMLElement, XMLText]]],
]


@pytest.fixture
def handler() -> HANDLER_TYPE:
    return_values = count()

    def handler_fct(
        node: Union[XMLElement, XMLText]
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield (f"handler-yield-{next(return_values)}", node)

    return handler_fct


def elem(
    name: str,
    *,
    attributes: Optional[Dict[str, str]] = None,
    parents: Tuple["XMLElement", ...] = (),
    namespace: str = "",
) -> XMLElement:
    return XMLElement(
        name,
        XMLElementAttributes(attributes or {}),
        parents,
        namespace,
    )


root_node = elem("root")


@pytest.mark.parametrize(
    ["xml", "node"],
    [
        (b"<root />", root_node),
        (b"<root></root>", root_node),
        (b"<root>Hello!</root>", root_node),
        (b"<root><foo><bar/></foo></root>", root_node),
        (
            b"<root abc='def' ghi='klm' />",
            elem("root", attributes={"abc": "def", "ghi": "klm"}),
        ),
        (
            b"<root xmlns='https://example.com/xml/' />",
            elem("root", namespace="https://example.com/xml/"),
        ),
    ],
    ids=["self-closing", "empty", "with text", "with children", "attributes", "xmlns"],
)
def test_root_level(
    xml: bytes,
    node: XMLElement,
    # pylint: disable=redefined-outer-name
    handler: Callable[
        [Union[XMLElement, XMLText]],
        Iterator[Tuple[str, Union[XMLElement, XMLText]]],
    ],
) -> None:
    parser = Parser(xml)
    assert list(parser.iter_from(handler)) == [
        ("handler-yield-0", node),
    ]


elem_f_node = elem("foo", parents=(root_node,))
elem_b_node = elem("bar", parents=(root_node,), attributes={"abc": "def"})
text_h_node = XMLText("Hello", (root_node,))
text_w_node = XMLText("World", (root_node,))
text_pi_node = XMLText("π", (root_node,))

# to make sure that text are not in buffer, we generate huge texts
BIG_TEXT_LEN = 1_000_000


@pytest.mark.parametrize(
    ["xml_content", "nodes"],
    [
        (b"", []),
        (b"Hello", [text_h_node]),
        (b"<foo />", [elem_f_node]),
        (b"Hello<foo />", [text_h_node, elem_f_node]),
        (b"<foo />World", [elem_f_node, text_w_node]),
        (b"Hello<foo />World", [text_h_node, elem_f_node, text_w_node]),
        (
            b'Hello<foo />World<bar abc="def" />Hello',
            [text_h_node, elem_f_node, text_w_node, elem_b_node, text_h_node],
        ),
        (
            b"Hello<foo>Abc<bar>Def<xxx />Ghi</bar>Klm</foo>World",
            [text_h_node, elem_f_node, text_w_node],
        ),
        (
            b'%s<foo />%s<bar abc="def" />%s'
            % (
                b"a" * BIG_TEXT_LEN,
                b"b" * BIG_TEXT_LEN,
                b"c" * BIG_TEXT_LEN,
            ),
            [
                XMLText("a" * BIG_TEXT_LEN, (root_node,)),
                elem_f_node,
                XMLText("b" * BIG_TEXT_LEN, (root_node,)),
                elem_b_node,
                XMLText("c" * BIG_TEXT_LEN, (root_node,)),
            ],
        ),
    ],
    ids=[
        "empty",
        "text",
        "element",
        "text + element",
        "element + text",
        "text + element + text",
        "text + element + text + element + text",
        "depth",
        "big texts",
    ],
)
def test_content(
    xml_content: bytes,
    nodes: List[Union[XMLElement, XMLText]],
    # pylint: disable=redefined-outer-name
    handler: HANDLER_TYPE,
) -> None:
    @xml_handle_element("root")
    def root_handler(
        node: XMLElement,
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield from node.iter_from(handler)

    parser = Parser(b"<root>", xml_content, b"</root>")
    assert list(parser.iter_from(root_handler)) == [
        (f"handler-yield-{i}", node) for i, node in enumerate(nodes)
    ]


def test_out_of_order() -> None:
    @xml_handle_element("foo")
    def node_handler(node: XMLElement) -> Iterator[XMLElement]:
        yield node

    @xml_handle_element("root")
    def root_handler(node: XMLElement) -> Iterator[XMLElement]:
        yield from node.iter_from(node_handler)

    parser = Parser(b"<root><foo>hello</foo><foo>world</foo><foo>!</foo></root>")
    nodes = parser.iter_from(root_handler)
    first_node = next(nodes)
    second_node = next(nodes)
    assert second_node.text == "world"
    with pytest.raises(RuntimeError):
        first_node.text  # pylint: disable=pointless-statement  # noqa: B018


def test_many_small_streams(
    # pylint: disable=redefined-outer-name
    handler: HANDLER_TYPE,
) -> None:
    xml = b"<root>Hello<foo />World</root>"
    xml_parts = [bytes([v]) for v in xml]  # characters one by one
    assert len(xml_parts) == 30

    nodes = [text_h_node, elem_f_node, text_w_node]

    @xml_handle_element("root")
    def root_handler(
        node: XMLElement,
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield from node.iter_from(handler)

    parser = Parser(*xml_parts)
    assert list(parser.iter_from(root_handler)) == [
        (f"handler-yield-{i}", node) for i, node in enumerate(nodes)
    ]


def test_insecurely_allow_entities(
    # pylint: disable=redefined-outer-name
    handler: HANDLER_TYPE,
) -> None:
    xml = b'<!DOCTYPE money [<!ENTITY pi "&#960;">]><root>&pi;</root>'

    @xml_handle_element("root")
    def root_handler(
        node: XMLElement,
    ) -> Iterator[Tuple[str, Union[XMLElement, XMLText]]]:
        yield from node.iter_from(handler)

    with pytest.warns(UserWarning):
        parser = Parser(xml, insecurely_allow_entities=True)

    assert list(parser.iter_from(root_handler)) == [("handler-yield-0", text_pi_node)]
