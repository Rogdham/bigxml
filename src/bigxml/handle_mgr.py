from collections.abc import Iterable, Iterator
import sys
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, overload

from bigxml.handler_creator import create_handler
from bigxml.typing import (
    ClassHandlerWithCustomWrapper0,
    ClassHandlerWithCustomWrapper1,
    T,
)
from bigxml.utils import last_item_or_none

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import Never
else:  # pragma: no cover
    from typing import Never

if TYPE_CHECKING:
    from bigxml.nodes import XMLElement, XMLText


class HandleMgr:
    _handle: Optional[
        Callable[
            [Callable[[Union["XMLElement", "XMLText"]], Iterator[Any]]],
            Iterator[Any],
        ]
    ] = None

    # iter_from

    @overload
    def iter_from(
        self,
    ) -> Iterator["Never"]: ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            str,
            list[str],
            tuple[str, ...],
        ],
    ) -> Iterator["XMLElement"]: ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            type[ClassHandlerWithCustomWrapper0[T]],
            type[ClassHandlerWithCustomWrapper1[T]],
        ],
    ) -> Iterator[T]: ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            type[ClassHandlerWithCustomWrapper0[T]],
            type[ClassHandlerWithCustomWrapper1[T]],
            type[T],
        ],
    ) -> Iterator[T]: ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            type[ClassHandlerWithCustomWrapper0[T]],
            type[ClassHandlerWithCustomWrapper1[T]],
            str,
            list[str],
            tuple[str, ...],
        ],
    ) -> Iterator[Union["XMLElement", T]]: ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            type[ClassHandlerWithCustomWrapper0[T]],
            type[ClassHandlerWithCustomWrapper1[T]],
            type[T],
            str,
            list[str],
            tuple[str, ...],
        ],
    ) -> Iterator[Union["XMLElement", T]]: ...

    @overload  # type: ignore[misc]
    def iter_from(
        self,
        *handlers: Any,  # noqa: ANN401
    ) -> Iterator[object]: ...

    def iter_from(self, *handlers: Any) -> Iterator[object]:
        if not self._handle:
            raise RuntimeError("No handle to use")
        handler = create_handler(*handlers)
        return self._handle(handler)

    # return_from

    @overload
    def return_from(
        self,
    ) -> None: ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            str,
            list[str],
            tuple[str, ...],
        ],
    ) -> Optional["XMLElement"]: ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            type[ClassHandlerWithCustomWrapper0[T]],
            type[ClassHandlerWithCustomWrapper1[T]],
        ],
    ) -> Optional[T]: ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            type[ClassHandlerWithCustomWrapper0[T]],
            type[ClassHandlerWithCustomWrapper1[T]],
            type[T],
        ],
    ) -> Optional[T]: ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            type[ClassHandlerWithCustomWrapper0[T]],
            type[ClassHandlerWithCustomWrapper1[T]],
            str,
            list[str],
            tuple[str, ...],
        ],
    ) -> Optional[Union["XMLElement", T]]: ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            type[ClassHandlerWithCustomWrapper0[T]],
            type[ClassHandlerWithCustomWrapper1[T]],
            str,
            list[str],
            tuple[str, ...],
            type[T],
        ],
    ) -> Optional[Union["XMLElement", T]]: ...

    @overload
    def return_from(
        self,
        *handlers: object,
    ) -> Optional[object]: ...

    def return_from(self, *handlers: Any) -> Optional[Any]:
        return last_item_or_none(self.iter_from(*handlers))
