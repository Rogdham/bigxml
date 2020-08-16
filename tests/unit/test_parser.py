from io import BytesIO
from itertools import count
from unittest.mock import Mock, call
import pytest

from bigxml.elements import XMLElement, XMLText
from bigxml.parser import parse


@pytest.fixture
def handler():
    mock = Mock()
    return_values = count()
    mock.side_effect = lambda _: ("handler-yield-{}".format(next(return_values)),)
    yield mock


root_node = XMLElement("root", {}, ())


@pytest.mark.parametrize(
    "xml, node",
    [
        [b"<root />", root_node],
        [b"<root></root>", root_node],
        [b"<root>Hello!</root>", root_node],
        [b"<root><foo><bar/></foo></root>", root_node],
        [
            b"<root abc='def' ghi='klm' />",
            XMLElement("root", {"abc": "def", "ghi": "klm"}, ()),
        ],
        [
            b"<root xmlns='http://www.example.com/xml/' />",
            XMLElement("root", {}, (), "http://www.example.com/xml/"),
        ],
    ],
    ids=["self-closing", "empty", "with text", "with children", "attributes", "xmlns"],
)
def test_root_level(xml, node, handler):  # pylint: disable=redefined-outer-name
    parsed = parse(BytesIO(xml), handler)
    assert list(parsed) == ["handler-yield-0"]
    handler.assert_called_once_with(node)


elem_f_node = XMLElement("foo", {}, (root_node,))
elem_b_node = XMLElement("bar", {"abc": "def"}, (root_node,))
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
            % (b"a" * BIG_TEXT_LEN, b"b" * BIG_TEXT_LEN, b"c" * BIG_TEXT_LEN,),
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
        yield from node.handle(handler)

    parsed = parse(BytesIO(b"<root>%s</root>" % xml_contents), root_handler)
    assert list(parsed) == ["handler-yield-{}".format(i) for i in range(len(nodes))]
    assert handler.call_args_list == [call(node) for node in nodes]
