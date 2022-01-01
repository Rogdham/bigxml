# Recipes

## Working with _Requests_ {: #requests }

[_Requests_][requests] is a library that simplifies making HTTP requests.

It is easy to stream an XML response from a server and parse it on the fly:

- When creating the request, specify [`stream=True`][requests request] so that the
  content is downloaded as needed if the server supports it;
- Instead of getting the content from the response at once, use
  [`Response.iter_content`][requests response.iter_content] to iterate over the response
  data in chunks.

[requests]: https://requests.readthedocs.io/
[requests request]: https://requests.readthedocs.io/en/master/api/#requests.request
[requests response.iter_content]:
  https://requests.readthedocs.io/en/master/api/#requests.Response.iter_content

<!---->

    :::python
    >>> @xml_handle_element("root", "item")
    ... def handler(node):
    ...     yield node.text

    >>> response = requests.get("https://example.com/placeholder.xml", stream=True)
    >>> parser = Parser(response.iter_content(1 << 14))

    >>> for item in parser.iter_from(handler):
    ...     print(item)
    This example shows parsing in streaming with Requests.
    It works quite well!

!!! Note "Performance optimizations"

    The number passed to `Response.iter_content` is the chunk size, which is the maximum
    number of bytes that will be obtained at a time. This specific value of `1 << 14` is
    the one used under the hood by _BigXML_'s parsing library. Although any size would
    work, use anything between 1kb and 1Mb for best results.

## Dataclasses {: #dataclass }

Although not mandatory, using a [dataclass] may seem natural to hold the parsed data:

[dataclass]: https://docs.python.org/3/library/dataclasses.html

    :::xml filename=users.xml
    <users>
        <user id="13">
            <firstname>Alice</firstname>
            <lastname>Cooper</lastname>
        </user>
        <user id="37">
            <firstname>Bob</firstname>
            <lastname>Marley</lastname>
        </user>
        <user id="42">
            <firstname>Carol</firstname>
        </user>
    </users>

<!---->

    :::python
    >>> from dataclasses import dataclass

    >>> @xml_handle_element("users", "user")
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

    >>> with open("users.xml", "rb") as stream:
    ...     for user in Parser(stream).iter_from(User):
    ...         print(user)
    User(firstname='Alice', lastname='Cooper')
    User(firstname='Bob', lastname='Marley')
    User(firstname='Carol', lastname='N/A')

!!! Warning

    All fields of the dataclass must have a default value.

If you need to get information from the node handled by the dataclass, you can do so in
the `__post_init__` method:

    :::python
    >>> from dataclasses import dataclass, InitVar

    >>> @xml_handle_element("users", "user")
    ... @dataclass
    ... class User:
    ...     node: InitVar
    ...     id: int = 0
    ...     firstname: str = 'N/A'
    ...     lastname: str = 'N/A'
    ...
    ...     def __post_init__(self, node):
    ...         self.id = int(node.attributes['id'])
    ...
    ...     @xml_handle_element("firstname")
    ...     def handle_firstname(self, node):
    ...         self.firstname = node.text
    ...
    ...     @xml_handle_element("lastname")
    ...     def handle_lastname(self, node):
    ...         self.lastname = node.text

    >>> with open("users.xml", "rb") as stream:
    ...     for user in Parser(stream).iter_from(User):
    ...         print(user)
    User(id=13, firstname='Alice', lastname='Cooper')
    User(id=37, firstname='Bob', lastname='Marley')
    User(id=42, firstname='Carol', lastname='N/A')

!!! Warning

    The `node` attribute is an `InitVar`, so that it is passed to `__post_init__` but
    not stored in class attributes. It must be the only mandatory field, since the class
    is automatically instantiated with only one argument (the node). For more details,
    see [class handlers](handlers.md#classes).

## Yielding data in a class `__init__` {: #yield-in-init }

If you use a [class handler](handlers.md#classes), you may want to yield some data when
the class starts or ends to parse nodes. Of course, it is not possible to use the
`yield` keyword in `__init__`:

    :::python
    >>> @xml_handle_element("root", "cart")
    ... class Cart:
    ...     def __init__(self, node):
    ...         yield f"START cart parsing for user {node.attributes['user']}"

    >>> with open("carts.xml", "rb") as stream:
    ...     for item in Parser(stream).iter_from(Cart):
    ...         print(item)
    Traceback (most recent call last):
        ...
    TypeError: __init__() should return None...

Instead, you can define a custom `xml_handler` method:

    :::python
    >>> @xml_handle_element("root", "cart")
    ... class Cart:
    ...     def __init__(self, node):
    ...         self.user = node.attributes["user"]
    ...
    ...     @xml_handle_element("product")
    ...     def handle_product(self, node):
    ...         yield f"product: {node.text}"
    ...
    ...     def xml_handler(self, items):
    ...         yield f"START cart parsing for user {self.user}"
    ...         yield from items
    ...         yield f"END cart parsing for user {self.user}"

    >>> with open("carts.xml", "rb") as stream:
    ...     for item in Parser(stream).iter_from(Cart):
    ...         print(item)
    START cart parsing for user Alice
    product: 9781846975769
    product: 9780008322052
    END cart parsing for user Alice
    START cart parsing for user Bob
    product: 9780008117498
    product: 9780340960196
    product: 9780099580485
    END cart parsing for user Bob

## Streams without root {: #no-root }

In some cases, you may be parsing a stream of XML elements that follow each other
without starting with a common root.

For example, let's say a software outputs the following log file:

    :::xml filename=log.xml
    <log level="WARN">Main reactor overheat</log>
    <log level="INFO">Starting emergency coolers</log>
    <log level="DEBUG">Cooler 4 is online</log>
    <log level="DEBUG">Cooler 2 is online</log>
    <log level="INFO">Main reactor temperature is back to an acceptable level</log>

We can just wrap the stream in an XML element:

    :::python
    >>> @xml_handle_element("root", "log")
    ... def handler(node):
    ...     yield f"{node.attributes['level']:5} {node.text}"

    >>> with open("log.xml", "rb") as stream:
    ...     parser = Parser(b"<root>", stream, b"</root>")
    ...     for item in parser.iter_from(handler):
    ...         print(item)
    WARN  Main reactor overheat
    INFO  Starting emergency coolers
    DEBUG Cooler 4 is online
    DEBUG Cooler 2 is online
    INFO  Main reactor temperature is back to an acceptable level

## Infinite streams {: #infinite-streams }

Infinite streams are supported through file-like objects and iterables.

Here is an example using an infinite generator function as a stream:

    :::python
    >>> def collatz_generator(value):
    ...     yield b"<root>"
    ...     while True:
    ...         yield b"<item>%d</item>" % value
    ...         if value % 2:
    ...             value = 3 * value + 1
    ...         else:
    ...             value //= 2

    >>> stream = collatz_generator(42)

    >>> @xml_handle_element("root", "item")
    ... def handler(node):
    ...     yield int(node.text)

    >>> items = Parser(stream).iter_from(handler)
    >>> for _ in range(12):
    ...     print(next(items))
    42
    21
    64
    32
    16
    8
    4
    2
    1
    4
    2
    1
