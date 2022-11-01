# Handlers

The methods `iter_from` and `return_from` take _handlers_ as arguments.

## Functions

A handler can be a generator function taking a _node_ as an argument.

Such functions are usually decorated with `xml_handle_element` or `xml_handle_text`, to
restrict the type of nodes they are called with.

    :::xml filename=inventory.xml
    <inventory>
        <book>9780261103573</book>
        <lego ean="5702014975200">79005</lego>
        <dvd>0883929452996</dvd>
    </inventory>

<!---->

    :::python
    >>> @xml_handle_element("inventory", "book")
    ... @xml_handle_element("inventory", "dvd")
    ... def handle_ean(node):
    ...     yield (node.text, node.name)

    >>> @xml_handle_element("inventory", "lego")
    ... def handle_lego(node):
    ...     yield (node.attributes["ean"], "toy")

    >>> with open("inventory.xml", "rb") as stream:
    ...     for ean, kind in Parser(stream).iter_from(handle_ean, handle_lego):
    ...         print(f"{ean} ({kind})")
    9780261103573 (book)
    5702014975200 (toy)
    0883929452996 (dvd)

!!! Note

    To handle different kinds of nodes at once, the same function can be decorated
    several times with `xml_handle_element` or `xml_handle_text` as shown above.

## Classes

Passing a class as a handler is a good way to group the handling of a node and its
children.

!!! Note

    Although not mandatory, using a [dataclass] feels quite natural in most cases. See
    [this recipe](recipes.md#dataclass) for more information.

[dataclass]: https://docs.python.org/3/library/dataclasses.html

Let's parse the following XML file:

    :::xml filename=carts.xml
    <root>
        <cart user="Alice">
            <product price="7.35">9781846975769</product>
            <product price="2.12">9780008322052</product>
        </cart>
        <cart user="Bob">
            <product price="4.99">9780008117498</product>
            <product price="8.14">9780340960196</product>
            <product price="7.37">9780099580485</product>
        </cart>
    </root>

### Class instantiation

The class is instantiated automatically when a matching node is encountered:

    :::python
    >>> @xml_handle_element("root", "cart")
    ... class Cart:
    ...     pass

    >>> with open("carts.xml", "rb") as stream:
    ...     for instance in Parser(stream).iter_from(Cart):
    ...         print(instance)
    <__main__.Cart object...>
    <__main__.Cart object...>

If your class has an `__init__` method taking one mandatory parameter as argument, that
argument is supplied with the encountered node:

    :::python
    >>> @xml_handle_element("root", "cart")
    ... class Cart:
    ...     def __init__(self, node):
    ...         self.user = node.attributes["user"]

    >>> with open("carts.xml", "rb") as stream:
    ...     for instance in Parser(stream).iter_from(Cart):
    ...         print(f"{instance} for user {instance.user}")
    <__main__.Cart object...> for user Alice
    <__main__.Cart object...> for user Bob

### Class methods as sub-handlers

The methods decorated with `xml_handle_element` or `xml_handle_text` are used as
sub-handlers:

    :::python
    >>> @xml_handle_element("root", "cart")
    ... class Cart:
    ...     def __init__(self):
    ...         self.price = 0.0
    ...
    ...     @xml_handle_element("product")
    ...     def handle_product(self, node):
    ...         self.price += float(node.attributes["price"])

    >>> with open("carts.xml", "rb") as stream:
    ...     for instance in Parser(stream).iter_from(Cart):
    ...         print(f"{instance} total {instance.price:.2f}")
    <__main__.Cart object...> total 9.47
    <__main__.Cart object...> total 20.50

!!! Note

    If such a class method yields some items, they are ignored and a warning message is
    issued. This behavior can be changed as explained below.

### Changing yielded items

As seen above, the class handler yields the class instance. This default behavior can be
changed by implementing an `xml_handler` method:

    :::python
    >>> @xml_handle_element("root", "cart")
    ... class Cart:
    ...     def __init__(self, node):
    ...         self.user = node.attributes["user"]
    ...         self.price = 0.0
    ...
    ...     @xml_handle_element("product")
    ...     def handle_product(self, node):
    ...         self.price += float(node.attributes["price"])
    ...
    ...     def xml_handler(self):
    ...         yield (self.user, self.price)

    >>> with open("carts.xml", "rb") as stream:
    ...     for user, price in Parser(stream).iter_from(Cart):
    ...         print(f"{user} total {price:.2f}")
    Alice total 9.47
    Bob total 20.50

You can add a single mandatory parameter to `xml_handler`. In that case, it will be an
iterator whose items are yielded by the sub-handlers.

We can rewrite a previous example to leverage this behavior:

    :::python
    >>> @xml_handle_element("root", "cart")
    ... class Cart:
    ...     @xml_handle_element("product")
    ...     def handle_product(self, node):
    ...         yield float(node.attributes["price"])
    ...
    ...     def xml_handler(self, iterator):
    ...         yield sum(iterator)

    >>> with open("carts.xml", "rb") as stream:
    ...     for price in Parser(stream).iter_from(Cart):
    ...         print(price)
    9.47
    20.50

!!! Warning

    The children of the node handled by the class instance are parsed as the same time
    as the iterator is being iterated over. It is up to you to consume the iterator and
    consider the side-effects your methods may have.

!!! Tip "See also"

    - [Read this recipe](recipes.md#yield-in-init) if you want to yield some items in
      the `__init__` method
    - [Another recipe](recipes.md#dataclass) discusses usage with [dataclasses]

[dataclasses]: https://docs.python.org/3/library/dataclasses.html

## Syntactic sugar

To avoid creating a handler that simply yields the node, the following handler types are
available:

`tuple` of `str` / `list` of `str`

: `("html", "body", "p")` is equivalent to the following handler:

        :::python
        @xml_handle_element("html", "body", "p")
        def handler(node):
            yield node

`str`

: `"p"` is equivalent to `["p"]` or to the following handler:

        :::python
        @xml_handle_element("p")
        def handler(node):
            yield node

This allows to quickly iterate over a specific type of children of the current node:

    :::python
    >>> @xml_handle_element("root", "cart")
    ... def handler(node):
    ...     yield (
    ...         node.attributes["user"],
    ...         sum(
    ...             float(subnode.attributes["price"])
    ...             for subnode in node.iter_from("product")
    ...         )
    ...     )

    >>> with open("carts.xml", "rb") as stream:
    ...     for user, price in Parser(stream).iter_from(handler):
    ...         print(f"{user} total {price:.2f}")
    Alice total 9.47
    Bob total 20.50
