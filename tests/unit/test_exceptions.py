from typing import Iterator

from defusedxml import DefusedXmlException, NotSupportedError
from defusedxml.ElementTree import ParseError
import pytest

from bigxml.exceptions import BigXmlError, rewrite_exceptions


def generate(ex: Exception) -> Iterator[int]:
    yield 42
    raise ex


@pytest.mark.parametrize(
    ["exception", "msg", "security"],
    [
        pytest.param(
            ParseError(ValueError("something went wrong")),
            "Something went wrong",
            False,
            id="ParseError",
        ),
        pytest.param(
            DefusedXmlException("something went wrong"),
            "Invalid XML",
            True,
            id="DefusedXmlException",
        ),
        pytest.param(
            NotSupportedError(),
            "The operation is not supported",
            True,
            id="NotSupportedError",
        ),
    ],
)
def test_exceptions(exception: Exception, msg: str, security: bool) -> None:
    iterator = rewrite_exceptions(generate(exception))
    assert next(iterator) == 42
    with pytest.raises(BigXmlError) as exc_info:
        next(iterator)
    assert str(exc_info.value) == msg
    assert exc_info.value.security == security
