import sys
from typing import Any, Callable, Iterable, Iterator, Optional, Type, TypeVar, Union

if sys.version_info < (3, 8):  # pragma: no cover
    from typing_extensions import Protocol
else:  # pragma: no cover
    from typing import Protocol

if sys.version_info < (3, 10):  # pragma: no cover
    from typing_extensions import ParamSpec
else:  # pragma: no cover
    from typing import ParamSpec


# pylint: disable=invalid-name, unused-argument


P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
F = TypeVar("F", bound=Callable[..., Any])
K = TypeVar("K", bound=Type[Any])

T_co = TypeVar("T_co", covariant=True)


class SupportsRead(Protocol[T_co]):
    def read(self, size: Optional[int] = None) -> T_co:
        ...  # pragma: no cover


# cyclic types are not supported yet
StreamableRec5 = Any
StreamableRec4 = Union[SupportsRead[bytes], bytes, Iterable[StreamableRec5]]
StreamableRec3 = Union[SupportsRead[bytes], bytes, Iterable[StreamableRec4]]
StreamableRec2 = Union[SupportsRead[bytes], bytes, Iterable[StreamableRec3]]
StreamableRec1 = Union[SupportsRead[bytes], bytes, Iterable[StreamableRec2]]
StreamableRec0 = Union[SupportsRead[bytes], bytes, Iterable[StreamableRec1]]
Streamable = Union[SupportsRead[bytes], bytes, Iterable[StreamableRec0]]


class ClassHandlerWithCustomWrapper0(Protocol[T_co]):
    def xml_handler(self) -> Optional[Iterable[T_co]]:
        ...  # pragma: no cover


class ClassHandlerWithCustomWrapper1(Protocol[T_co]):
    def xml_handler(self, items: Iterator[Any]) -> Optional[Iterable[T_co]]:
        ...  # pragma: no cover
