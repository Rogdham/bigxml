from bigxml.utils import last_item_or_none


class HandleMgr:
    _handle_fct = None

    def set_handle(self, handle):
        self._handle_fct = handle

    def iter_from(self, handler):
        if not self._handle_fct:
            raise RuntimeError("No handle to use")
        return self._handle_fct(handler)

    def return_from(self, handler):
        return last_item_or_none(self.iter_from(handler))
