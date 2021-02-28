import pytest

from bigxml import Parser, xml_handle_element

XML = b"""
<root xmlns="http://example.com/xml/"
    xmlns:ex="http://example.com/xml/ex"
    xmlns:other="http://example.com/xml/other">
    <aaa>Nodes inherit namespaces</aaa>
    <aaa xmlns="http://example.com/xml/aaa">Overriding namespace</aaa>
    <ex:aaa>Overriding namespace bis</ex:aaa>
    <bbb uuu="0" ex:vvv="1" xxx="2" ex:xxx="3" other:xxx="4" ex:yyy="5" other:yyy="6">
        Looking for attributes
    </bbb>
</root>
"""


def test_namespaces():
    class Handler:

        #
        # namespaces in element names
        #

        # using `aaa` handle all {*}aaa unless overridden
        @staticmethod
        @xml_handle_element("root", "aaa")
        def handle_aaa(node):
            yield ("aaa", node.namespace)

        # using `{...}aaa` overrides `aaa` handler
        @staticmethod
        @xml_handle_element("root", "{http://example.com/xml/ex}aaa")
        def handle_aaa_ex(node):
            yield ("aaa_ex", node.namespace)

        # using `{}aaa` overrides `aaa` handler when there is no namespace
        @staticmethod
        @xml_handle_element("root", "{}aaa")
        def handle_aaa_no_namespace(node):
            # this code is never run
            yield ("aaa_no_namespace", node.namespace)

        #
        # namespaces in element attributes
        #

        @staticmethod
        @xml_handle_element("root", "bbb")
        def handle_bbb(node):
            # `name` gets any namespace
            # `{ns}name` gets specific namespace
            # `{}name` gets no namespace
            yield ("bbb", "uuu default", node.attributes["uuu"])
            yield ("bbb", "uuu no", node.attributes["{}uuu"])
            yield ("bbb", "vvv default", node.attributes["vvv"])
            yield (
                "bbb",
                "vvv specific",
                node.attributes["{http://example.com/xml/ex}vvv"],
            )
            # `name` prefers to get no namespace when possible
            yield ("bbb", "xxx default", node.attributes["xxx"])  # -> 2
            yield ("bbb", "xxx no", node.attributes["{}xxx"])
            yield (
                "bbb",
                "xxx specific",
                node.attributes["{http://example.com/xml/ex}xxx"],
            )
            # note that a warning is emitted if there are attributes with various
            # namespaces but none without namespace
            with pytest.warns(RuntimeWarning):
                # current implementation uses "first" attribute in that case
                # but you should not rely on it and specify the namespace to use
                yield ("bbb", "yyy default", node.attributes["yyy"])

    assert list(Parser(XML).iter_from(Handler)) == [
        ("aaa", "http://example.com/xml/"),
        ("aaa", "http://example.com/xml/aaa"),
        ("aaa_ex", "http://example.com/xml/ex"),
        ("bbb", "uuu default", "0"),
        ("bbb", "uuu no", "0"),
        ("bbb", "vvv default", "1"),
        ("bbb", "vvv specific", "1"),
        ("bbb", "xxx default", "2"),
        ("bbb", "xxx no", "2"),
        ("bbb", "xxx specific", "3"),
        ("bbb", "yyy default", "5"),
    ]
