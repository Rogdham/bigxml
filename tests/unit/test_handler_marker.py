import pytest

from bigxml.handler_marker import _ATTR_MARKER, xml_handle_element, xml_handle_text
from bigxml.nodes import XMLText


def test_one_maker_element():
    @xml_handle_element("abc", "def")
    def fct(arg):
        return arg * 6

    assert getattr(fct, _ATTR_MARKER, None) == (("abc", "def"),)
    assert fct(7) == 42


def test_one_maker_element_on_method():
    class Klass:
        def __init__(self, multiplier):
            self.multiplier = multiplier

        @xml_handle_element("abc", "def")
        def method(self, arg):
            return arg * self.multiplier

    instance = Klass(6)
    assert getattr(instance.method, _ATTR_MARKER, None) == (("abc", "def"),)
    assert instance.method(7) == 42


def test_one_maker_element_on_static_method():
    class Klass:
        @xml_handle_element("abc", "def")
        @staticmethod
        def method(arg):
            return arg * 6

    assert getattr(Klass.method, _ATTR_MARKER, None) == (("abc", "def"),)
    assert Klass.method(7) == 42


def test_one_maker_element_on_method_before_staticmethod():
    class Klass:
        @staticmethod
        @xml_handle_element("abc", "def")
        def method(arg):
            return arg * 6

    assert getattr(Klass.method, _ATTR_MARKER, None) == (("abc", "def"),)
    assert Klass.method(7) == 42


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


def test_one_marker_text_no_call():
    @xml_handle_text
    def fct(arg):
        return arg * 6

    assert getattr(fct, _ATTR_MARKER, None) == ((XMLText.name,),)
    assert fct(7) == 42


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
