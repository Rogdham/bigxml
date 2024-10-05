__ATTR_MARK_NAME = "_xml_handlers_on"


def has_marks(obj: object) -> bool:
    return hasattr(obj, __ATTR_MARK_NAME)


def get_marks(obj: object) -> tuple[tuple[str, ...], ...]:
    return getattr(obj, __ATTR_MARK_NAME, ())


def add_mark(obj: object, mark: tuple[str, ...]) -> None:
    marks = get_marks(obj)
    marks += (mark,)
    setattr(obj, __ATTR_MARK_NAME, marks)
