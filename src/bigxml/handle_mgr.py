from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    overload,
)

from bigxml.handler_creator import create_handler
from bigxml.typing import (
    ClassHandlerWithCustomWrapper0,
    ClassHandlerWithCustomWrapper1,
    T,
)
from bigxml.utils import last_item_or_none

if TYPE_CHECKING:
    import sys

    from bigxml.nodes import XMLElement, XMLText

    if sys.version_info < (3, 11):  # pragma: no cover
        from typing import NoReturn as Never
    else:  # pragma: no cover
        from typing import Never


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
    ) -> Iterator["Never"]:
        # we don't have '...' as body in this overload as a workaround
        # to prevent 'not-an-iterable' error in pylint
        # see https://github.com/PyCQA/astroid/issues/1015
        return iter(())

    @overload
    def iter_from(
        self,
        *handlers: Union[
            str,
            List[str],
            Tuple[str, ...],
        ],
    ) -> Iterator["XMLElement"]:
        ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            Type[ClassHandlerWithCustomWrapper0[T]],
            Type[ClassHandlerWithCustomWrapper1[T]],
        ],
    ) -> Iterator[T]:
        ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            Type[ClassHandlerWithCustomWrapper0[T]],
            Type[ClassHandlerWithCustomWrapper1[T]],
            Type[T],
        ],
    ) -> Iterator[T]:
        ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            Type[ClassHandlerWithCustomWrapper0[T]],
            Type[ClassHandlerWithCustomWrapper1[T]],
            str,
            List[str],
            Tuple[str, ...],
        ],
    ) -> Iterator[Union["XMLElement", T]]:
        ...

    @overload
    def iter_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            Type[ClassHandlerWithCustomWrapper0[T]],
            Type[ClassHandlerWithCustomWrapper1[T]],
            Type[T],
            str,
            List[str],
            Tuple[str, ...],
        ],
    ) -> Iterator[Union["XMLElement", T]]:
        ...

    @overload
    def iter_from(
        self,
        *handlers: Any,  # noqa: ANN401
    ) -> Iterator[object]:
        ...

    def iter_from(self, *handlers: Any) -> Iterator[object]:
        if not self._handle:
            raise RuntimeError("No handle to use")
        handler = create_handler(*handlers)
        return self._handle(handler)  # pylint: disable=not-callable

    # return_from

    @overload
    def return_from(
        self,
    ) -> None:
        ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            str,
            List[str],
            Tuple[str, ...],
        ],
    ) -> Optional["XMLElement"]:
        ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            Type[ClassHandlerWithCustomWrapper0[T]],
            Type[ClassHandlerWithCustomWrapper1[T]],
        ],
    ) -> Optional[T]:
        ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            Type[ClassHandlerWithCustomWrapper0[T]],
            Type[ClassHandlerWithCustomWrapper1[T]],
            Type[T],
        ],
    ) -> Optional[T]:
        ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            Type[ClassHandlerWithCustomWrapper0[T]],
            Type[ClassHandlerWithCustomWrapper1[T]],
            str,
            List[str],
            Tuple[str, ...],
        ],
    ) -> Optional[Union["XMLElement", T]]:
        ...

    @overload
    def return_from(
        self,
        *handlers: Union[
            Callable[[Union["XMLElement", "XMLText"]], Optional[Iterable[T]]],
            ClassHandlerWithCustomWrapper0[T],
            ClassHandlerWithCustomWrapper1[T],
            Type[ClassHandlerWithCustomWrapper0[T]],
            Type[ClassHandlerWithCustomWrapper1[T]],
            str,
            List[str],
            Tuple[str, ...],
            Type[T],
        ],
    ) -> Optional[Union["XMLElement", T]]:
        ...

    @overload
    def return_from(
        self,
        *handlers: object,
    ) -> Optional[object]:
        ...

    def return_from(self, *handlers: Any) -> Optional[Any]:
        return last_item_or_none(self.iter_from(*handlers))
