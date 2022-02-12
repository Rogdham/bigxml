from bigxml.marks import add_mark
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

        add_mark(markable, tuple(args))

        return obj

    return wrapper


def xml_handle_text(*args):
    # @xml_handle_text
    if len(args) == 1 and callable(args[0]):  # https://stackoverflow.com/q/653368
        return xml_handle_element(XMLText.name)(args[0])

    # @xml_handle_text(...)
    return xml_handle_element(*args, XMLText.name)
