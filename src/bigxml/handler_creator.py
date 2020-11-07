from bigxml.nodes import XMLElement
from bigxml.utils import dictify

_ATTR_MARKER = "_xml_handlers_on"


def handler_from_dict(handler_dict):
    def handle(node):
        handler = None
        if hasattr(node, "namespace"):
            handler = handler_dict.get(f"{{{node.namespace}}}{node.name}")
        if handler is None:
            handler = handler_dict.get(node.name)
        value = None
        if handler is not None:
            if isinstance(handler, dict):
                if isinstance(node, XMLElement):
                    sub_handler = handler_from_dict(handler)
                    value = node.iter_from(sub_handler)
            else:
                value = handler(node)
        if value is None:
            # e.g. handler without return value
            return ()  # empty iterable
        # we assume handler returns iterable
        return value

    return handle


def join_handlers(*handlers):
    handler_dict = dictify(*handlers)
    return handler_from_dict(handler_dict)
