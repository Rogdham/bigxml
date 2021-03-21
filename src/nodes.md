# Nodes

A _node_ is the representation of an XML element or character data (i.e. text).

They are passed as the argument to [handlers](handlers.md) functions.

    :::xml
    <p>Hello, world!</p>

The XML document above has two nodes:

- An element node of name `p`;
- A text node of text `Hello, world!`, whose parent if the previous node.

## XMLElement

`name`

: The name of the element, without the [namespace].

`namespace`

: The namespace of the element (or an empty string if no [namespace]).

`attributes`

: The attributes of the node as a `dict`-like object.

`parents`

: All parents of the node, in order, as a `tuple` of `XMLElement` instances.

`iter_from`, `return_from`

: Methods to handle the children of the node, [same as `Parser` instances](parser.md).

`text`

: A property to get a `str` representation of the text of the node.

    !!! Warning

        Using the `text` property parses all the children of the XML element until the
        closing element is found. As a result, you have to choose between calling
        `iter_from`, `return_from`, or accessing the `text` property, otherwise
        [an exception](faq.md#exnodes-out-of-order-exception) will be raised.

[namespace]: ./namespaces.md

## XMLText

`text`

: The text of the node.

`parents`

: All parents of the node, in order, as a `tuple` of `XMLElement` instances.
