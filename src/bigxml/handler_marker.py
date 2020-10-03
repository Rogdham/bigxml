from bigxml.handler_creator import _ATTR_MARKER
from bigxml.nodes import XMLText


def xml_handle_element(*args):
    if not args:
        raise TypeError("Call to xml_handle_element without any args")

    def wrapper(obj):
        markable = obj

        if isinstance(markable, staticmethod):
            # staticmethod(xml_handle_element(...)) works as expected
            # xml_handle_element(staticmethod(...)) needs special care
            markable = markable.__func__

        markers = getattr(markable, _ATTR_MARKER, ())
        setattr(markable, _ATTR_MARKER, markers + (tuple(args),))

        return obj

    return wrapper


def xml_handle_text(*args):
    return xml_handle_element(*args, XMLText.name)
