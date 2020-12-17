from bigxml.handler_creator import create_handler
from bigxml.utils import last_item_or_none


class HandleMgr:
    _handle_fct = None

    def set_handle(self, handle):
        self._handle_fct = handle

    def iter_from(self, *handlers):
        if not self._handle_fct:
            raise RuntimeError("No handle to use")
        handler = create_handler(*handlers)
        return self._handle_fct(handler)

    def return_from(self, *handlers):
        return last_item_or_none(self.iter_from(*handlers))
