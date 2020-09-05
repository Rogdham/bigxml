import pytest

from bigxml.handler import _ATTR_MARKER, xml_handle_element, xml_handle_text
from bigxml.nodes import XMLText


def test_one_maker_element():
    @xml_handle_element("abc", "def")
    def fct(arg):
        return arg * 6

    assert getattr(fct, _ATTR_MARKER, None) == (("abc", "def"),)
    assert fct(7) == 42


def test_several_maker_element():
    @xml_handle_element("abc", "def")
    @xml_handle_element("ghi")
    @xml_handle_element("klm", "opq", "rst")
    def fct(arg):
        return arg * 6

    assert getattr(fct, _ATTR_MARKER, None) == (
        ("klm", "opq", "rst"),
        ("ghi",),
        ("abc", "def"),
    )
    assert fct(7) == 42


def test_one_maker_element_no_args():
    with pytest.raises(TypeError):

        @xml_handle_element()
        def fct(arg):  # pylint: disable=unused-variable
            return arg * 6


def test_one_marker_text_no_args():
    @xml_handle_text()
    def fct(arg):
        return arg * 6

    assert getattr(fct, _ATTR_MARKER, None) == ((XMLText.name,),)
    assert fct(7) == 42


def test_one_marker_text_args():
    @xml_handle_text("abc", "def")
    def fct(arg):
        return arg * 6

    assert getattr(fct, _ATTR_MARKER, None) == (
        (
            "abc",
            "def",
            XMLText.name,
        ),
    )
    assert fct(7) == 42


def test_mixed_markers():
    @xml_handle_element("abc", "def")
    @xml_handle_text("ghi")
    @xml_handle_element("klm", "opq", "rst")
    def fct(arg):
        return arg * 6

    assert getattr(fct, _ATTR_MARKER, None) == (
        ("klm", "opq", "rst"),
        ("ghi", XMLText.name),
        ("abc", "def"),
    )
    assert fct(7) == 42
