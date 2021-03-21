# Frequently Asked Questions

## What does opening a file in binary mode means? {: #parse-file-binary }

By default, when you call `open("filename.xml")`, the file is open in text mode. In this
mode, the content of the file is returned as a string: the bytes are decoded on the fly.

However, _BigXML_ needs `bytes`-oriented [streams](streams.md), so you need to open the
file in binary mode by explicitly specifying it with an extra parameter:
`open("filename.xml", "rb")`.

    :::xml filename=hello.xml
    <root>Hello, world!</root>

<!---->

    :::python
    >>> @xml_handle_element("root")
    ... def handler(node):
    ...     yield node.text

    >>> # BAD
    >>> with open("hello.xml") as f:
    ...    Parser(f).return_from(handler)
    Traceback (most recent call last):
        ...
    TypeError: Stream read method returned a str, not a bytes-like object.
               Open file objects in binary mode.

    >>> # GOOD
    >>> with open("hello.xml", "rb") as f:
    ...    Parser(f).return_from(handler)
    'Hello, world!'

## How can I parse a string? {: #parse-str }

Just convert `str` into `bytes` using `.encode` or `codecs.encode`:

    :::python
    >>> @xml_handle_element("root")
    ... def handler(node):
    ...     yield node.text
    ...
    >>> stream_str = "<root>Hello, world!</root>"

    >>> # BAD
    >>> Parser(stream_str).return_from(handler)
    Traceback (most recent call last):
        ...
    TypeError: Invalid stream type: str.
               Convert it to a bytes-like object by encoding it.

    >>> # GOOD
    >>> Parser(stream_str.encode()).return_from(handler)
    'Hello, world!'

!!! Tip

    Read the error message!

## I keep getting the following exception: Tried to access a node out of order {: #exnodes-out-of-order-exception }

Each byte of the XML streams is only read once. An exception occurs when you try to
perform an action that would need to go backward in the streams. For more details,
[read the philosophy behind the design of _BigXML_](index.md#philosophy).

Usually, the issue can be solved by following these principles:

- Consider that all children of a node must be processed in one pass;
- You usually want to handle an `XMLElement` instance as soon as you receive it;
- The `text` property of a `XMLElement` node needs to access all its children, so using
  it prevents you from calling `iter_from` and `return_from` on the same node.

For example, consider the following piece of code:

    :::xml filename=user.xml
    <user>
        <firstname>Alice</firstname>
        <lastname>Cooper</lastname>
    </user>

<!---->

    :::python
    >>> @xml_handle_element("firstname")
    ... def handle_firstname(node):
    ...     yield node.text

    >>> @xml_handle_element("lastname")
    ... def handle_lastname(node):
    ...     yield node.text

    >>> @xml_handle_element("user")
    ... def handle_user(node):
    ...     firstname = node.return_from(handle_firstname)
    ...     lastname = node.return_from(handle_lastname)
    ...     yield f"{firstname} {lastname}"

    >>> with open("user.xml", "rb") as f:
    ...    Parser(f).return_from(handle_user)
    Traceback (most recent call last):
        ...
    RuntimeError: Tried to access a node out of order

The issue occurred because the children of the `user` node are read twice:

- A first time to obtain a `firstname` child;
- A second time to obtain a `lastname` child.

Instead, we need to consider the `firstname` and `lastname` children at the same time:

    :::python
    >>> @xml_handle_element("user")
    ... def handle_user(node):
    ...     names = {}
    ...     for child_node in node.iter_from("firstname", "lastname"):
    ...         names[child_node.name] = child_node.text
    ...     yield f"{names['firstname']} {names['lastname']}"

    >>> with open("user.xml", "rb") as f:
    ...    Parser(f).return_from(handle_user)
    'Alice Cooper'

The code above is hardly readable; you probably want to use a
[class handler](handlers.md#classes) instead:

    :::python
    >>> from dataclasses import dataclass

    >>> @xml_handle_element("user")
    ... @dataclass
    ... class User:
    ...     firstname: str = 'N/A'
    ...     lastname: str = 'N/A'
    ...
    ...     @xml_handle_element("firstname")
    ...     def handle_firstname(self, node):
    ...         self.firstname = node.text
    ...
    ...     @xml_handle_element("lastname")
    ...     def handle_lastname(self, node):
    ...         self.lastname = node.text
    ...
    ...     def xml_handler(self):
    ...         yield f"{self.firstname} {self.lastname}"

    >>> with open("user.xml", "rb") as f:
    ...    Parser(f).return_from(User)
    'Alice Cooper'

## I have an other issue, or a feature request

By all means, [open an issue](https://github.com/rogdham/bigxml/issues) on GitHub!
