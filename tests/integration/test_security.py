from typing import Iterator

from defusedxml import EntitiesForbidden
import pytest

from bigxml import Parser, XMLText


def handler_get_text(node: XMLText) -> Iterator[str]:
    yield node.text


@pytest.mark.parametrize(
    "xml",
    (
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a "bigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbigbig">\n'
                b"]>\n"
                b"<root>&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;</root>\n"
            ),
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
            id="recursive",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a SYSTEM "file:///etc/hosts">\n'
                b"]>\n"
                b"<root>&a;</root>\n"
            ),
            id="resolution (file)",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a SYSTEM "https://example.com/">\n'
                b"]>\n"
                b"<root>&a;</root>\n"
            ),
            id="resolution (http)",
        ),
        pytest.param(
            (
                b"<!DOCTYPE foobar [\n"
                b'    <!ENTITY a SYSTEM "expect://id">\n'
                b"]>\n"
                b"<root>&a;</root>\n"
            ),
            id="resolution (expect)",
        ),
    ),
)
def test_external_entities(xml: bytes) -> None:
    with pytest.raises(EntitiesForbidden):
        Parser(xml).return_from(handler_get_text)
