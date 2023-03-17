import pytest

from bigxml import BigXmlError, Parser


@pytest.mark.parametrize(
    ["xml", "msg"],
    [
        pytest.param(
            b"",
            "No element found: line 1, column 0",
            id="Empty",
        ),
        pytest.param(
            b"Lorem ipsum dolor sit amet",
            "Syntax error: line 1, column 0",
            id="Not XML",
        ),
        pytest.param(
            b"<root><item>value</item></root",
            "Unclosed token: line 1, column 24",
            id="Truncated",
        ),
        pytest.param(
            b"<root>\xe0\xe9\xef\xf4\xf9</root>",
            "Not well-formed (invalid token): line 1, column 6",
            id="Encoding",
        ),
    ],
)
def test_invalid_xml(xml: bytes, msg: str) -> None:
    parser = Parser(xml)
    iterable = parser.iter_from("node")
    with pytest.raises(BigXmlError) as exc_info:
        next(iterable)
    assert str(exc_info.value) == msg
    assert not exc_info.value.security

    parser = Parser(xml)
    with pytest.raises(BigXmlError) as exc_info:
        parser.return_from("node")
    assert str(exc_info.value) == msg
    assert not exc_info.value.security
