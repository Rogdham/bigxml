from typing import Callable, Iterator, Union
from unittest.mock import Mock

import pytest

from bigxml.nodes import XMLElement, XMLText


def create_text(text: str) -> XMLText:
    return XMLText(text, ())  # don't care about parents


def create_element(*children: Union[XMLElement, XMLText]) -> XMLElement:
    node = XMLElement("foo", Mock(), ())  # don't care about parents
    handle = Mock()

    def side_effect(
        handler: Callable[
            [Union[XMLElement, XMLText]], Iterator[Union[XMLElement, XMLText]]
        ]
    ) -> Iterator[Union[XMLElement, XMLText]]:
        for child in children:
            yield from handler(child)

    handle.side_effect = side_effect
    node._handle = handle  # pylint: disable=protected-access
    return node


@pytest.mark.parametrize("text", ["abc", "  \n  abc \n  "])
def test_element_get_text_direct(text: str) -> None:
    node = create_element(create_text(text))
    assert node.text == "abc"


@pytest.mark.parametrize(
    ["left", "middle", "right", "exp"],
    [
        ("a", "b", "c", "abc"),
        ("a ", " b ", " c", "a b c"),
        ("a ", "b", " c", "a b c"),
        ("a", " b ", "c", "a b c"),
        ("a", "", "c", "ac"),
        ("a", " ", "c", "ac"),
        ("a ", "", "c", "a c"),
        ("a", "", " c", "a c"),
        ("a ", "", " c", "a c"),
    ],
)
def test_element_get_text_nested(left: str, middle: str, right: str, exp: str) -> None:
    node = create_element(
        create_text(left),
        create_element(create_text(middle)),
        create_text(right),
    )
    assert node.text == exp
