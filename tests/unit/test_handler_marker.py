from typing import Iterator, Union

import pytest

from bigxml.handler_marker import xml_handle_element, xml_handle_text
from bigxml.marks import get_marks
from bigxml.nodes import XMLElement, XMLText


def test_one_maker_element() -> None:
    @xml_handle_element("abc", "def")
    def fct(node: XMLElement) -> Iterator[str]:
        yield f"<{node.text}>"

    assert get_marks(fct) == (("abc", "def"),)


def test_one_maker_element_on_method() -> None:
    class Klass:
        def __init__(self, multiplier: int) -> None:
            self.multiplier = multiplier

        @xml_handle_element("abc", "def")
        def method(self, node: XMLElement) -> Iterator[str]:
            yield f"<{node.text}>" * self.multiplier

    instance = Klass(6)
    assert get_marks(instance.method) == (("abc", "def"),)


def test_one_maker_element_on_static_method() -> None:
    class Klass:
        @xml_handle_element("abc", "def")
        @staticmethod
        def method(node: XMLElement) -> Iterator[str]:
            yield f"<{node.text}>"

    assert get_marks(Klass.method) == (("abc", "def"),)


def test_one_maker_element_on_method_before_staticmethod() -> None:
    class Klass:
        @staticmethod
        @xml_handle_element("abc", "def")
        def method(node: XMLElement) -> Iterator[str]:
            yield f"<{node.text}>"

    assert get_marks(Klass.method) == (("abc", "def"),)


def test_several_maker_element() -> None:
    @xml_handle_element("abc", "def")
    @xml_handle_element("ghi")
    @xml_handle_element("klm", "opq", "rst")
    def fct(node: XMLElement) -> Iterator[str]:
        yield f"<{node.text}>"

    assert get_marks(fct) == (
        ("klm", "opq", "rst"),
        ("ghi",),
        ("abc", "def"),
    )


def test_one_maker_element_no_args() -> None:
    with pytest.raises(TypeError):

        @xml_handle_element()
        def fct(node: XMLElement) -> Iterator[str]:
            yield f"<{node.text}>"


def test_one_marker_text_no_call() -> None:
    @xml_handle_text
    def fct(node: XMLText) -> Iterator[str]:
        yield f"<{node.text}>"

    assert get_marks(fct) == ((XMLText.name,),)


def test_one_marker_text_no_args() -> None:
    @xml_handle_text()
    def fct(node: XMLText) -> Iterator[str]:
        yield f"<{node.text}>"

    assert get_marks(fct) == ((XMLText.name,),)


def test_one_marker_text_args() -> None:
    @xml_handle_text("abc", "def")
    def fct(node: XMLText) -> Iterator[str]:
        yield f"<{node.text}>"

    assert get_marks(fct) == (
        (
            "abc",
            "def",
            XMLText.name,
        ),
    )


def test_mixed_markers() -> None:
    @xml_handle_element("abc", "def")
    @xml_handle_text("ghi")
    @xml_handle_element("klm", "opq", "rst")
    def fct(node: Union[XMLElement, XMLText]) -> Iterator[str]:
        yield f"<{node.text}>"

    assert get_marks(fct) == (
        ("klm", "opq", "rst"),
        ("ghi", XMLText.name),
        ("abc", "def"),
    )
