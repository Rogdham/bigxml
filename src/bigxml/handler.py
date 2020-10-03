from bigxml.handler_creator import _ATTR_MARKER, join_handlers


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
