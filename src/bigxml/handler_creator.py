from inspect import getmembers, isclass
import warnings

from bigxml.utils import (
    consume,
    dictify,
    get_mandatory_params,
    transform_none_return_value,
)

_ATTR_MARKER = "_xml_handlers_on"
CLASS_HANDLER_METHOD_NAME = "xml_handler"


def _test_one_mandatory_param(mandatory_params, method_name):
    if len(mandatory_params) > 1:
        raise TypeError(
            f"Invalid class method: {method_name}"
            " should have no or one mandatory parameters, got:"
            f" {', '.join(mandatory_params)}"
        )


def _handler_identity(node):
    yield node


def _handle_from_leaf(leaf):
    # class
    if isclass(leaf):
        init_mandatory_params = get_mandatory_params(leaf)
        _test_one_mandatory_param(init_mandatory_params, "__init__")

        def handle(node):
            instance = leaf(node) if init_mandatory_params else leaf()
            sub_handle = transform_none_return_value(_handle_from_leaf(instance))
            items = sub_handle(node)

            wrapper = getattr(instance, CLASS_HANDLER_METHOD_NAME, None)
            if wrapper is None:
                return items

            wrapper_mandatory_params = get_mandatory_params(wrapper)
            _test_one_mandatory_param(
                wrapper_mandatory_params,
                CLASS_HANDLER_METHOD_NAME,
            )

            if wrapper_mandatory_params:
                return wrapper(items)

            if consume(items):
                warnings.warn(
                    (
                        "Items were yielded by some sub-handler"
                        f" of class {instance.__class__.__name__}."
                        f" Add an argument to {CLASS_HANDLER_METHOD_NAME}"
                        " to handle them properly."
                    ),
                    RuntimeWarning,
                )

            return wrapper()

        return handle

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
