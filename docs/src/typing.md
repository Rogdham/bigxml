# Typing

_BigXML_ commes natively with type hints, which are checked by [_mypy_][mypy].

The benefits are twofold:

- Improve the correctness of the code of the library itself;
- Allow users of the library to benefit from well-defined type hints on the public API.

As a rule of thumbs, we follow [Postel's law][postels_law] by being as vague as possible
for the arguments of functions, and as precise as possible for the returned values.

[mypy]: https://mypy.readthedocs.io/en/stable/index.html
[postels_law]: https://en.wikipedia.org/wiki/Robustness_principle

## Handlers

    :::python
    >>> from typing import Iterator, Tuple

    >>> @xml_handle_text("p")
    ... def handle_text(node: XMLText) -> Iterator[str]:
    ...     yield node.text

    >>> @xml_handle_element("p", "em")
    ... def handle_em(node: XMLElement) -> Iterator[str]:
    ...     yield node.text

    >>> @xml_handle_element("root", "cart")
    ... class Cart:
    ...     @xml_handle_element("product")
    ...     def handle_product(self, node: XMLElement) -> Iterator[float]:
    ...         yield float(node.attributes["price"])
    ...
    ...     def xml_handler(self, iterator: Iterator[float]) -> Iterator[float]:
    ...         yield sum(iterator)

!!! Note

    Instead of `Iterator[X]`, any iterable as return value works, as well as `None`.
    `Optional[Iterable[X]]` can also be used if needed.

## Returned values from `iter_from` / `return_from`

We our trying our best to be as specific as possible with the returned values of
`iter_from` and `return_from` methods.

    :::python
    >>> with open("paragraph.xml", "rb") as f:
    ...    for item in Parser(f).iter_from(handle_text, handle_em):
    ...        print(type(item), repr(item))
    ...        # reveal_type(item)
    ...        # Revealed type is "builtins.str"
    <class 'str'> '\n    Hello,\n    '
    <class 'str'> 'world'
    <class 'str'> '\n    !\n'

However, there are some cases where a little help from your side is needed.

### Several handlers with no common type in return value

    :::xml filename=mixed.xml
    <root>
        <number>42</number>
        <string>Abc</string>
    </root>

<!---->

    :::python
    >>> @xml_handle_text("root", "number")
    ... def handle_number(node: XMLText) -> Iterator[int]:
    ...     yield int(node.text)

    >>> @xml_handle_text("root", "string")
    ... def handle_string(node: XMLText) -> Iterator[str]:
    ...     yield node.text

    >>> with open("mixed.xml", "rb") as f:
    ...    for item in Parser(f).iter_from(handle_number, handle_string):
    ...        print(type(item), item)
    ...        # reveal_type(item)
    ...        # Revealed type is "builtins.object"
    <class 'int'> 42
    <class 'str'> Abc

Here we can see that the type of `item` is `object`, which is not precise.

In that case, instead of just using `cast`, you can use the provided `HandlerTypeHelper`
with the expected type in square brackets, by simply adding it as one of the handlers
passed to `iter_from` or `return_from`:

    :::python
    >>> from typing import Union

    >>> with open("mixed.xml", "rb") as f:
    ...    for item in Parser(f).iter_from(
    ...        HandlerTypeHelper[Union[int, str]],
    ...        handle_number,
    ...        handle_string,
    ...    ):
    ...        print(type(item), item)
    ...        # reveal_type(item)
    ...        # Revealed type is "Union[builtins.int, builtins.str]"
    <class 'int'> 42
    <class 'str'> Abc
