from bigxml.nodes import XMLElement, XMLText
from bigxml.utils import dictify

_ATTR_MARKER = "_xml_handlers_on"


#
# handler creators
#


def handler_from_dict(handler_dict):
    def handle(node):
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


#
# handler markers
#


def xml_handle_element(*args):
    if not args:
        raise TypeError("Call to xml_handle_element without any args")

    def wrapper(obj):
        markers = getattr(obj, _ATTR_MARKER, ())
        setattr(obj, _ATTR_MARKER, markers + (tuple(args),))
        return obj

    return wrapper


def xml_handle_text(*args):
    return xml_handle_element(*args, XMLText.name)


#
# handler class
#


class XMLHandler:
    def _xml_get_handlers(self):
        for handler_name in dir(self):
            if handler_name.startswith("__"):
                continue
            handler = getattr(self, handler_name)
            for handler_on in getattr(handler, _ATTR_MARKER, ()):
                yield (handler_on, handler)

    def __call__(self, node):
        handler = join_handlers(self._xml_get_handlers())
        return handler(node)
