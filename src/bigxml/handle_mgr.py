class HandleMgr:
    _handle_fct = None

    def set_handle(self, handle):
        self._handle_fct = handle

    def iter_from(self, handler):
        # make sure handle fct is available
        handle_fct = self._handle_fct
        if not handle_fct:
            raise RuntimeError("No handle to use. Maybe you called handle already?")
        self._handle_fct = None

        # run the handle fct
        return handle_fct(handler)
