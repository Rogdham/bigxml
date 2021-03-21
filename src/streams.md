# Streams

A _stream_ is an object that can be passed as an argument to `Parser`. It represents the
raw XML data to be parsed.

## File-like objects

Files open **in binary mode**, `io.BytesIO`, etc.

    :::xml filename=hello.xml
    <root>Hello, world!</root>

<!---->

    :::python
    >>> @xml_handle_element("root")
    ... def handler(node):
    ...     yield node.text

    >>> with open("hello.xml", "rb") as stream:
    ...     Parser(stream).return_from(handler)
    'Hello, world!'

## Bytes-like objects

`bytes`, `bytearray`, `memoryview`, etc.

    :::python
    >>> @xml_handle_element("root")
    ... def handler(node):
    ...     yield node.text

    >>> stream = b"<root>Hello, world!</root>"

    >>> Parser(stream).return_from(handler)
    'Hello, world!'

## Iterables

Any iterable whose items are _streams_: lists, generators, etc.

    :::python
    >>> @xml_handle_element("root")
    ... def handler(node):
    ...     yield node.text

    >>> def generate_stream():
    ...     yield b"<root>"
    ...     yield b"Hello, world!"
    ...     yield b"</root>"

    >>> stream = generate_stream()

    >>> Parser(stream).return_from(handler)
    'Hello, world!'

More examples:

- [HTTP streaming with _Requests_](recipes.md#requests)
- [Infinite stream](recipes.md#infinite-streams)

!!! Note

    You can pass any number of streams to `Parser`, so the following are equivalent:

    - `Parser([stream0, stream1, stream2])`
    - `Parser(stream0, stream1, stream2)`
