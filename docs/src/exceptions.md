# Exceptions

All exceptions raised due to invalid stream content will be `BigXmlError` instances:

    :::python
    >>> Parser(b"").return_from()
    Traceback (most recent call last):
        ...
    bigxml.exceptions.BigXmlError: No element found: line 1, column 0

The `security` attribute on the `BigXmlError` instance is a boolean allowing you to
quickly know if the error came from a security issue when parsing the XML.

!!! Note

    Invalid usages of the library (e.g. passing a `str` to `Parser`) will raise other
    kinds of exceptions.
