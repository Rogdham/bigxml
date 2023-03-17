from typing import Iterator, Tuple

import pytest

from bigxml import Parser, XMLElement, xml_handle_element

XML = b"""
<root xmlns="https://example.com/xml/"
    xmlns:ex="https://example.com/xml/ex"
    xmlns:other="https://example.com/xml/other">
    <aaa>Nodes inherit namespaces</aaa>
    <aaa xmlns="https://example.com/xml/aaa">Overriding namespace</aaa>
    <ex:aaa>Overriding namespace bis</ex:aaa>
    <bbb uuu="0" ex:vvv="1" xxx="2" ex:xxx="3" other:xxx="4" ex:yyy="5" other:yyy="6">
        Looking for attributes
    </bbb>
</root>
"""


def test_namespaces() -> None:
    class Handler:
        #
        # namespaces in element names
        #

        # using `aaa` handle all {*}aaa unless overridden
        @staticmethod
        @xml_handle_element("root", "aaa")
        def handle_aaa(node: XMLElement) -> Iterator[Tuple[str, str, str]]:
            yield ("aaa", node.namespace, "")

        # using `{...}aaa` overrides `aaa` handler
        @staticmethod
        @xml_handle_element("root", "{https://example.com/xml/ex}aaa")
        def handle_aaa_ex(node: XMLElement) -> Iterator[Tuple[str, str, str]]:
            yield ("aaa_ex", node.namespace, "")

        # using `{}aaa` overrides `aaa` handler when there is no namespace
        @staticmethod
        @xml_handle_element("root", "{}aaa")
        def handle_aaa_no_namespace(node: XMLElement) -> Iterator[Tuple[str, str, str]]:
            # this code is never run
            yield ("aaa_no_namespace", node.namespace, "")

        #
        # namespaces in element attributes
        #

        @staticmethod
        @xml_handle_element("root", "bbb")
        def handle_bbb(node: XMLElement) -> Iterator[Tuple[str, str, str]]:
            # `name` gets any namespace
            # `{ns}name` gets specific namespace
            # `{}name` gets no namespace
            yield ("bbb", "uuu default", node.attributes["uuu"])
            yield ("bbb", "uuu no", node.attributes["{}uuu"])
            yield ("bbb", "vvv default", node.attributes["vvv"])
            yield (
                "bbb",
                "vvv specific",
                node.attributes["{https://example.com/xml/ex}vvv"],
            )
            # `name` prefers to get no namespace when possible
            yield ("bbb", "xxx default", node.attributes["xxx"])  # -> 2
            yield ("bbb", "xxx no", node.attributes["{}xxx"])
            yield (
                "bbb",
                "xxx specific",
                node.attributes["{https://example.com/xml/ex}xxx"],
            )
            # note that a warning is emitted if there are attributes with various
            # namespaces but none without namespace
            with pytest.warns(UserWarning):
                # current implementation uses "first" attribute in that case
                # but you should not rely on it and specify the namespace to use
                yield ("bbb", "yyy default", node.attributes["yyy"])

        @staticmethod
        def xml_handler(
            generator: Iterator[Tuple[str, str, str]]
        ) -> Iterator[Tuple[str, str, str]]:
            yield from generator

    assert list(Parser(XML).iter_from(Handler)) == [
        ("aaa", "https://example.com/xml/", ""),
        ("aaa", "https://example.com/xml/aaa", ""),
        ("aaa_ex", "https://example.com/xml/ex", ""),
        ("bbb", "uuu default", "0"),
        ("bbb", "uuu no", "0"),
        ("bbb", "vvv default", "1"),
        ("bbb", "vvv specific", "1"),
        ("bbb", "xxx default", "2"),
        ("bbb", "xxx no", "2"),
        ("bbb", "xxx specific", "3"),
        ("bbb", "yyy default", "5"),
    ]
