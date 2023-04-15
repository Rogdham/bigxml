from typing import Iterator

import pytest

from bigxml import BigXmlError, Parser, XMLText


def handler_get_text(node: XMLText) -> Iterator[str]:
    yield node.text


@pytest.mark.parametrize(
    ["xml", "msg"],
    [
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a "bigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbig">\n'
                b"]>\n"
                b"<root>&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;</root>\n"
            ),
            "Entity definition is forbidden",
            id="one entity (1kb)",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a "bigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbig">\n'
                b'    <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">\n'
                b'    <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">\n'
                b'    <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;">\n'
                b'    <!ENTITY e "&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;">\n'
                b"]>\n"
                b"<root>&e;</root>\n"
            ),
            "Entity definition is forbidden",
            id="bomb (5Mb)",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a "bigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbig">\n'
                b'    <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">\n'
                b'    <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">\n'
                b'    <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;">\n'
                b'    <!ENTITY e "&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;">\n'
                b'    <!ENTITY f "&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;&e;">\n'
                b'    <!ENTITY g "&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;&f;">\n'
                b'    <!ENTITY h "&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;&g;">\n'
                b"]>\n"
                b"<root>&h;</root>\n"
            ),
            "Entity definition is forbidden",
            id="bomb (33Gb)",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a "something &b;">\n'
                b'    <!ENTITY b "&a;">\n'
                b"]>\n"
                b"<root>&a;</root>\n"
            ),
            "Entity definition is forbidden",
            id="recursive",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a SYSTEM "file:///etc/hosts">\n'
                b"]>\n"
                b"<root>&a;</root>\n"
            ),
            "Entity definition is forbidden",
            id="resolution (file)",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a SYSTEM "https://example.com/">\n'
                b"]>\n"
                b"<root>&a;</root>\n"
            ),
            "Entity definition is forbidden",
            id="resolution (http)",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a SYSTEM "expect://id">\n'
                b"]>\n"
                b"<root>&a;</root>\n"
            ),
            "Entity definition is forbidden",
            id="resolution (expect)",
        ),
    ],
)
def test_external_entities(xml: bytes, msg: str) -> None:
    with pytest.raises(BigXmlError) as exc_info:
        Parser(xml).return_from(handler_get_text)
    assert str(exc_info.value) == msg
    assert exc_info.value.security


def test_insecurely_allow_entities() -> None:
    xml = (
        b"<!DOCTYPE foobar [\n"
        b'    <!ENTITY Omega "&#937;">\n'
        b"]>\n"
        b"<root>&Omega;</root>\n"
    )
    with pytest.warns(UserWarning):
        parser = Parser(xml, insecurely_allow_entities=True)
    value = parser.return_from(handler_get_text)
    assert value == "Ω"
