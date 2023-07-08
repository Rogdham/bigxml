from functools import partial
from typing import Tuple

__ATTR_MARK_NAME = "_xml_handlers_on"


def _unwrap_partials(obj: object) -> object:
    if isinstance(obj, partial):
        return obj.func
    return obj


def has_marks(obj: object) -> bool:
    return hasattr(_unwrap_partials(obj), __ATTR_MARK_NAME)


def get_marks(obj: object) -> Tuple[Tuple[str, ...], ...]:
    return getattr(_unwrap_partials(obj), __ATTR_MARK_NAME, ())


def add_mark(obj: object, mark: Tuple[str, ...]) -> None:
    obj = _unwrap_partials(obj)
    marks = get_marks(obj)
    marks += (mark,)
    setattr(obj, __ATTR_MARK_NAME, marks)
