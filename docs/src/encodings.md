# Stream encodings

The [streams](streams.md) passed to `Parser` are expected to be `bytes`-oriented.

The decoding is performed according to the
[XML specification](https://www.w3.org/TR/xml/#charencoding), i.e. based on the
`encoding` attribute of the XML declaration:

    :::xml
    <?xml version='1.0' encoding='ISO-8859-1'?>

!!! Note

    The XML declaration is optional for UTF-8 and UTF-16 encodings.

## Wrong encoding

Sometimes, the encoding of the stream to parse does not match the one specified in the
XML declaration.

    :::python
    >>> @xml_handle_element("root")
    ... def handler(node):
    ...     yield node.text

    >>> stream_bytes = b"<root>\xe0\xe9\xef\xf4\xf9</root>"  # ISO-8859-1

    >>> Parser(stream_bytes).return_from(handler)
    Traceback (most recent call last):
        ...
    bigxml.exceptions.BigXmlError: Not well-formed (invalid token)...

If you know that there is no XML declaration, you can add one before the stream:

    :::python
    >>> Parser(
    ...    "<?xml version='1.0' encoding='ISO-8859-1'?>".encode("ISO-8859-1"),
    ...    stream_bytes,
    ... ).return_from(handler)
    'àéïôù'

But if the XML declaration is already here, you will need to change the encoding of your
stream manually. For `bytes` instances, decode then encode:

    :::python
    >>> stream_bytes_with_xml_declaration = (
    ...     b"<?xml version='1.0' encoding='UTF-8'?>"  # wrong encoding specified
    ...     b"<root>\xe0\xe9\xef\xf4\xf9</root>"       # ISO-8859-1
    ... )

    >>> Parser(
    ...     stream_bytes_with_xml_declaration.decode("ISO-8859-1").encode("UTF-8"),
    ... ).return_from(handler)
    'àéïôù'

For file-like objects, use `codecs.EncodedFile`:

    :::python
    >>> import io
    >>> stream_file = io.BytesIO(stream_bytes_with_xml_declaration)

    >>> import codecs
    >>> Parser(
    ...     codecs.EncodedFile(stream_file, "UTF-8", "ISO-8859-1"),
    ... ).return_from(handler)
    'àéïôù'
