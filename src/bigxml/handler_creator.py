from inspect import getmembers, isclass

from bigxml.utils import dictify, transform_none_return_value

_ATTR_MARKER = "_xml_handlers_on"


def _handler_identity(node):
    yield node


def _handle_from_leaf(leaf):
    # class
    if isclass(leaf):
        raise TypeError("Invalid handler type: class")

    # callable
    if callable(leaf):
        return leaf

    # object with markers on public methods
    handlers_with_markers = []
    for handler_name, handler in getmembers(leaf):
        if handler_name.startswith("__"):
            continue
        for marker in getattr(handler, _ATTR_MARKER, ()):
            handlers_with_markers.append((marker, handler))
    if handlers_with_markers:
        handler = _handler_from_tree(dictify(handlers_with_markers))
        if hasattr(leaf, _ATTR_MARKER):
            return lambda node: node.iter_from(handler)
        return handler

    raise TypeError(f"Invalid handler type: {type(leaf).__name__}")


def _handler_from_tree(handler_dict):
    def handle(node):
        handler = None
        if hasattr(node, "namespace"):
            handler = handler_dict.get(f"{{{node.namespace}}}{node.name}")
        if handler is None:
            handler = handler_dict.get(node.name)
        if handler is not None:
            if isinstance(handler, dict):
                if hasattr(node, "iter_from"):
                    sub_handler = _handler_from_tree(handler)
                    return node.iter_from(sub_handler)
            else:
                return _handle_from_leaf(handler)(node)
        return None

    return handle


def create_handler(*args):
    handlers_with_markers = []
    handlers_without_markers = []
    for arg in args:
        markers = getattr(arg, _ATTR_MARKER, None)
        if markers is None:
            # syntactic sugar cases
            if isinstance(arg, str):
                arg = (arg,)
            if isinstance(arg, list):
                arg = tuple(arg)
            if isinstance(arg, tuple):
                handlers_with_markers.append((arg, _handler_identity))

            # no markers
            else:
                handlers_without_markers.append(arg)
        else:
            # markers
            for marker in markers:
                handlers_with_markers.append((marker, arg))

    if handlers_without_markers:
        # both handlers with and without markers
        if handlers_with_markers:
            raise TypeError("Catchall handler with other non-catchall handlers")

        # multiple handlers without markers
        if len(handlers_without_markers) > 1:
            raise TypeError("Several catchall handlers")

        # only one handler without markers
        leaf = handlers_without_markers[0]
        handler = _handle_from_leaf(leaf)

    else:
        # only handlers with markers
        tree = dictify(handlers_with_markers)
        handler = _handler_from_tree(tree)

    # if handler returns None, makes it return empty iterable instead
    return transform_none_return_value(handler)
