# note: only used items are defined here

from xml.etree.ElementTree import Element, ParseError, iterparse

class DefusedXmlException(ValueError): ...  # noqa: N818

__all__ = ("DefusedXmlException", "Element", "iterparse", "ParseError")
