__ATTR_MARK_NAME = "_xml_handlers_on"


def has_marks(obj):
    return hasattr(obj, __ATTR_MARK_NAME)


def get_marks(obj):
    return getattr(obj, __ATTR_MARK_NAME, ())


def add_mark(obj, mark):
    marks = get_marks(obj)
    marks += (mark,)
    setattr(obj, __ATTR_MARK_NAME, marks)
