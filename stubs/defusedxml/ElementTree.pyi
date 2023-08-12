# ruff: noqa: FBT001
# note: only used items are defined here, with used typing

from typing import Iterator, Optional, Protocol, Sequence, TypeVar
from xml.etree.ElementTree import Element, ParseError

_T_co = TypeVar("_T_co", covariant=True)

class _SupportsRead(Protocol[_T_co]):
    def read(self, size: Optional[int] = None) -> _T_co: ...

def iterparse(
    source: _SupportsRead[bytes],
    events: Sequence[str] | None = None,
    forbid_dtd: bool = False,
    forbid_entities: bool = True,
    forbid_external: bool = False,
) -> Iterator[tuple[str, Element]]: ...

class DefusedXmlException(ValueError): ...  # noqa: N818

__all__ = ("DefusedXmlException", "Element", "iterparse", "ParseError")
