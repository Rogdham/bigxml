import xml.etree.ElementTree as ET

import pytest

from bigxml import Parser, xml_handle_element

TXT_STR = "aàâæcçeéèêëiïîoôuùûü"
XML_STR = f"<élément>{TXT_STR}</élément>"


@pytest.mark.parametrize(
    "xml",
    (
        # UTF-8 and UTF-16 may omit XML declaration (in which case BOM is optional for UTF-8)
        # https://www.w3.org/TR/xml/#charencoding
        pytest.param(
            XML_STR.encode("utf_8"),
            id="implicit UTF-8 without BOM",
        ),
        pytest.param(
            b"\xef\xbb\xbf" + XML_STR.encode("utf_8"),
            id="implicit UTF-8 with BOM",
        ),
        pytest.param(
            b"\xff\xfe" + XML_STR.encode("utf_16_le"),
            id="implicit UTF-16 (LE) with BOM",
        ),
        pytest.param(
            b"\xfe\xff" + XML_STR.encode("utf_16_be"),
            id="implicit UTF-16 (BE) with BOM",
        ),
        # various encodings with XML declaration
        pytest.param(
            ("<?xml version='1.0' encoding='UTF-8'?>" + XML_STR).encode("utf_8"),
            id="explicit UTF-8 without BOM",
        ),
        pytest.param(
            b"\xef\xbb\xbf"
            + ("<?xml version='1.0' encoding='UTF-8'?>" + XML_STR).encode("utf_8"),
            id="explicit UTF-8 with BOM",
        ),
        pytest.param(
            b"\xff\xfe"
            + ("<?xml version='1.0' encoding='UTF-16'?>" + XML_STR).encode("utf_16_le"),
            id="explicit UTF-16 (LE) with BOM",
        ),
        pytest.param(
            b"\xfe\xff"
            + ("<?xml version='1.0' encoding='UTF-16'?>" + XML_STR).encode("utf_16_be"),
            id="explicit UTF-16 (BE) with BOM",
        ),
        pytest.param(
            ("<?xml version='1.0' encoding='ISO-8859-1'?>" + XML_STR).encode("latin_1"),
            id="explicit ISO-8859-1",
        ),
    ),
)
def test_encoding(xml):
    @xml_handle_element("élément")
    def handler(node):
        yield node.text

    assert Parser(xml).return_from(handler) == TXT_STR


def test_wrong_explicit_encoding():
    xml = ("<?xml version='1.0' encoding='ISO-8859-1'?>" + XML_STR).encode("utf_8")
    parser = Parser(xml)
    with pytest.raises(ET.ParseError):
        parser.return_from()
