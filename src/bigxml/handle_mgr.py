import warnings


class HandleMgr:
    _handle_fct = None

    def set_handle(self, handle):
        self._handle_fct = handle

    def iter_from(self, handler):
        if not self._handle_fct:
            raise RuntimeError("No handle to use")
        return self._handle_fct(handler)

    def return_from(self, handler):
        for item in self.iter_from(handler):
            warnings.warn(
                "Handler returned non-empty generator: {} (item: {})".format(
                    self, item
                ),
                RuntimeWarning,
            )
        return handler
