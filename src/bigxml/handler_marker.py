from typing import Any, Callable, Generic, Iterable, Optional, Union, cast, overload

from bigxml.marks import add_mark
from bigxml.nodes import XMLElement, XMLText
from bigxml.typing import F, K, Protocol, T, T_co, U

# Typing note: both decorators assume that decorated functions take
# one of XMLElement or XMLText as input, but the returned function
# accepts both as inputs… this way we have strong expectations on
# decorated functions while working well with the typing of
# iter_from and return_from.

# Also, a lot of the typing complexity comes from the fact that
# decorators can be applied on both functions, methods & staticmethods
# plus xml_handle_text can be applied without parenthesis as well


# pylint: disable-next=invalid-name
class ___xml_handle_xxx_wrapped(Protocol[T_co]):  # noqa: N801
    # wrapper for classes
    @overload
    def __call__(
        self,
        obj: K,
    ) -> K:
        ...

    # wrapper for functions
    @overload
    def __call__(
        self,
        obj: Callable[[T_co], Optional[Iterable[T]]],
    ) -> Callable[[Union[XMLElement, XMLText]], Optional[Iterable[T]]]:
        ...

    # wrapper for methods
    @overload
    def __call__(
        self,
        obj: Callable[[U, T_co], Optional[Iterable[T]]],
    ) -> Callable[[U, Union[XMLElement, XMLText]], Optional[Iterable[T]]]:
        ...


def xml_handle_element(*args: str) -> ___xml_handle_xxx_wrapped[XMLElement]:
    if not args:
        raise TypeError("Call to xml_handle_element without any args")

    def wrapper(obj: F) -> F:
        markable = obj

        if isinstance(markable, staticmethod):
            # staticmethod(xml_handle_element(...)) works as expected
            # xml_handle_element(staticmethod(...)) needs special care
            markable = cast(F, markable.__func__)

        add_mark(markable, tuple(args))

        return obj

    return cast(
        ___xml_handle_xxx_wrapped[XMLElement],
        wrapper,
    )


# @xml_handle_text (for classes)
@overload
def xml_handle_text(
    obj: K,
) -> K:
    ...


# @xml_handle_text (for functions)
@overload
def xml_handle_text(
    obj: Callable[[XMLText], Optional[Iterable[T]]],
) -> Callable[[Union[XMLElement, XMLText]], Optional[Iterable[T]]]:
    ...


# @xml_handle_text (for methods)
@overload
def xml_handle_text(
    obj: Callable[[U, XMLText], Optional[Iterable[T]]],
) -> Callable[[U, Union[XMLElement, XMLText]], Optional[Iterable[T]]]:
    ...


# @xml_handle_text(...) (for functions & methods)
@overload
def xml_handle_text(*args: str) -> ___xml_handle_xxx_wrapped[XMLText]:
    ...


def xml_handle_text(*args: Any, **_kwargs: Any) -> Any:
    if _kwargs:  # pragma: no cover
        # the _kwargs in the signature is just to be compliant with the first overload
        # with python >= 3.8 we will be able to change that overload
        #    to use a positional-only argument (PEP 570)
        # see also: https://stackoverflow.com/a/72409226
        raise TypeError(
            f"xml_handle_text called with some unexpected keyword arguments: {tuple(_kwargs)}"
        )

    # @xml_handle_text
    if len(args) == 1 and callable(args[0]):  # https://stackoverflow.com/q/653368
        return xml_handle_element(XMLText.name)(args[0])

    # @xml_handle_text(...)
    if all(isinstance(arg, str) for arg in args):
        return xml_handle_element(*args, XMLText.name)

    raise TypeError(
        f"xml_handle_text called with invalid arguments: {args}"
    )  # pragma: no cover


@xml_handle_element("\0type-helper")  # \0 makes sure it is an invalid element name
class HandlerTypeHelper(Generic[T]):
    """
    Handler that helps with type hints.

    By adding HandlerTypeHelper[Union[**redacted**]], one can makes the type of
    returned values of iter_from/return_from more precise.

    See documentation for more details.
    """

    @staticmethod
    def xml_handler() -> Iterable[T]:  # pragma: no cover
        raise RuntimeError  # will never be called
