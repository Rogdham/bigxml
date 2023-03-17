# note: only used items are defined here

class DefusedXmlException(ValueError): ...  # noqa: N818
class NotSupportedError(DefusedXmlException): ...

__all__ = ("DefusedXmlException", "NotSupportedError")
