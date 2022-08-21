from collections import deque
from functools import wraps
from inspect import Parameter, signature
import re
from typing import Callable, Generator, Iterable, Iterator, Optional, Tuple, cast

from bigxml.typing import P, T, U


class IterWithRollback(Iterator[T]):
    def __init__(self, iterable: Iterable[T]) -> None:
        self.iteration = 0
        self._iterator = iter(iterable)
        self._can_rollback = False
        self._item_rollback = False
        self._last_item: T  # will be always set when read

    def __iter__(self) -> Iterator[T]:
        return self

    def rollback(self) -> None:
        if self._can_rollback:
            self.iteration -= 1
            self._can_rollback = False
            self._item_rollback = True

    def __next__(self) -> T:
        if not self._item_rollback:
            self._last_item = next(self._iterator)
        self.iteration += 1
        self._can_rollback = True
        self._item_rollback = False
        return self._last_item


_EXTRACT_NAMESPACE_REGEX = re.compile(r"^\{([^}]*)\}(.*)$")


def extract_namespace_name(name: str) -> Tuple[str, str]:
    match = _EXTRACT_NAMESPACE_REGEX.match(name)
    if match:
        return cast(Tuple[str, str], match.groups())
    return ("", name)


def last_item_or_none(iterable: Iterable[T]) -> Optional[T]:
    try:
        return deque(iterable, maxlen=1)[0]
    except IndexError:
        return None


def consume(iterable: Iterable[object]) -> bool:
    iterator = iter(iterable)
    try:
        next(iterator)
    except StopIteration:
        return False
    last_item_or_none(iterator)
    return True


def transform_to_iterator(
    fct: Callable[P, Optional[Iterable[T]]]
) -> Callable[P, Iterator[T]]:
    @wraps(fct)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> Iterator[T]:
        return_value = fct(*args, **kwargs)
        if return_value is None:
            return iter(())  # empty iterator
        return iter(return_value)

    return wrapped


def get_mandatory_params(fct: Callable[..., object]) -> Tuple[str, ...]:
    try:
        sig = signature(fct)
    except (ValueError, TypeError):
        return ()  # e.g. for built-in
    return tuple(
        param.name
        for param in sig.parameters.values()
        if param.kind
        in (
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.KEYWORD_ONLY,
        )
        and param.default == sig.empty
    )


def autostart_generator(
    fct: Callable[P, Generator[T, U, None]]
) -> Callable[P, Generator[T, U, None]]:
    @wraps(fct)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> Generator[T, U, None]:
        generator = fct(*args, **kwargs)
        next(generator)  # ignore first yielded value
        return generator

    return wrapped
