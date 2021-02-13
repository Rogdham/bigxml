from bigxml.handler_creator import create_handler
from bigxml.utils import last_item_or_none


class HandleMgr:
    _handle = None

    def iter_from(self, *handlers):
        if not self._handle:
            raise RuntimeError("No handle to use")
        handler = create_handler(*handlers)
        return self._handle(handler)  # pylint: disable=not-callable

    def return_from(self, *handlers):
        return last_item_or_none(self.iter_from(*handlers))
