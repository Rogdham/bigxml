from typing import Iterable, Iterator

from defusedxml import DefusedXmlException
from defusedxml.ElementTree import ParseError

from bigxml.typing import T


class BigXmlError(ValueError):
    """Error parsing XML content"""

    def __init__(self, msg: str, *, security: bool) -> None:
        # put only first letter of 'msg' in uppercase
        super().__init__(msg[:1].upper() + msg[1:])
        self.security = security


def rewrite_exceptions(iterable: Iterable[T]) -> Iterator[T]:
    try:
        yield from iterable
    except ParseError as ex:
        raise BigXmlError(str(ex), security=False) from ex
    except DefusedXmlException as ex:
        # defusedxml has usable wording in it's exception's doc
        # except for base DefusedXmlException
        msg = (ex.__doc__ or "").strip()
        # pylint: disable-next=unidiomatic-typecheck
        if not msg or type(ex) is DefusedXmlException:
            msg = "Invalid XML"
        raise BigXmlError(msg, security=True) from ex
