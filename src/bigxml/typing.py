from collections.abc import Iterable, Iterator
import sys
from typing import Any, Callable, Optional, Protocol, TypeVar, Union

if sys.version_info < (3, 10):  # pragma: no cover
    from typing_extensions import ParamSpec
else:  # pragma: no cover
    from typing import ParamSpec

if sys.version_info < (3, 12):  # pragma: no cover
    from typing_extensions import Buffer
else:  # pragma: no cover
    from collections.abc import Buffer

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
F = TypeVar("F", bound=Callable[..., Any])
K = TypeVar("K", bound=type[Any])

T_co = TypeVar("T_co", covariant=True)


class SupportsRead(Protocol[T_co]):
    def read(self, size: Optional[int] = None) -> T_co: ...  # pragma: no cover


Streamable = Union[Buffer, SupportsRead[bytes], Iterable["Streamable"]]


class ClassHandlerWithCustomWrapper0(Protocol[T_co]):
    def xml_handler(self) -> Optional[Iterable[T_co]]: ...  # pragma: no cover


class ClassHandlerWithCustomWrapper1(Protocol[T_co]):
    def xml_handler(
        self, items: Iterator[Any]
    ) -> Optional[Iterable[T_co]]: ...  # pragma: no cover
