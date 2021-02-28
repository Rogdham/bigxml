from itertools import count

import pytest

from bigxml.nodes import XMLElement, XMLElementAttributes, XMLText
from bigxml.parser import Parser


@pytest.fixture
def handler():
    return_values = count()

    def handler_fct(node):
        yield (f"handler-yield-{next(return_values)}", node)

    yield handler_fct


def elem(name, *, attributes=None, parents=(), namespace=""):
    return XMLElement(name, XMLElementAttributes(attributes or {}), parents, namespace)


root_node = elem("root")


@pytest.mark.parametrize(
    "xml, node",
    [
        [b"<root />", root_node],
        [b"<root></root>", root_node],
        [b"<root>Hello!</root>", root_node],
        [b"<root><foo><bar/></foo></root>", root_node],
        [
            b"<root abc='def' ghi='klm' />",
            elem("root", attributes={"abc": "def", "ghi": "klm"}),
        ],
        [
            b"<root xmlns='http://www.example.com/xml/' />",
            elem("root", namespace="http://www.example.com/xml/"),
        ],
    ],
    ids=["self-closing", "empty", "with text", "with children", "attributes", "xmlns"],
)
def test_root_level(xml, node, handler):  # pylint: disable=redefined-outer-name
    parser = Parser(xml)
    assert list(parser.iter_from(handler)) == [
        ("handler-yield-0", node),
    ]


elem_f_node = elem("foo", parents=(root_node,))
elem_b_node = elem("bar", parents=(root_node,), attributes={"abc": "def"})
text_h_node = XMLText("Hello", (root_node,))
text_w_node = XMLText("World", (root_node,))

# to make sure that text are not in buffer, we generate huge texts
BIG_TEXT_LEN = 1_000_000


@pytest.mark.parametrize(
    "xml_contents, nodes",
    [
        [b"", []],
        [b"Hello", [text_h_node]],
        [b"<foo />", [elem_f_node]],
        [b"Hello<foo />", [text_h_node, elem_f_node]],
        [b"<foo />World", [elem_f_node, text_w_node]],
        [b"Hello<foo />World", [text_h_node, elem_f_node, text_w_node]],
        [
            b'Hello<foo />World<bar abc="def" />Hello',
            [text_h_node, elem_f_node, text_w_node, elem_b_node, text_h_node],
        ],
        [
            b"Hello<foo>Abc<bar>Def<xxx />Ghi</bar>Klm</foo>World",
            [text_h_node, elem_f_node, text_w_node],
        ],
        [
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
        ],
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
def test_contents(xml_contents, nodes, handler):  # pylint: disable=redefined-outer-name
    def root_handler(node):
        yield from node.iter_from(handler)

    parser = Parser(b"<root>", xml_contents, b"</root>")
    assert list(parser.iter_from(root_handler)) == [
        (f"handler-yield-{i}", node) for i, node in enumerate(nodes)
    ]


def test_out_of_order():
    def node_handler(node):
        yield node

    def root_handler(node):
        yield from node.iter_from(node_handler)

    parser = Parser(b"<root><foo>hello</foo><foo>world</foo><foo>!</foo></root>")
    nodes = parser.iter_from(root_handler)
    first_node = next(nodes)
    second_node = next(nodes)
    assert second_node.text == "world"
    with pytest.raises(RuntimeError):
        first_node.text  # pylint: disable=pointless-statement


def test_many_small_streams(handler):  # pylint: disable=redefined-outer-name
    xml = b"<root>Hello<foo />World</root>"
    xml_parts = list(bytes([v]) for v in xml)  # characters one by one
    assert len(xml_parts) == 30

    nodes = [text_h_node, elem_f_node, text_w_node]

    def root_handler(node):
        yield from node.iter_from(handler)

    parser = Parser(*xml_parts)
    assert list(parser.iter_from(root_handler)) == [
        (f"handler-yield-{i}", node) for i, node in enumerate(nodes)
    ]
