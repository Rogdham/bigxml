# Namespaces

In XML, namespaces allow to differentiate between elements or attributes that would have
the same name otherwise.

## General case

In most cases, you don't want to care about namespaces when parsing some XML.

When you see `foo:bar` in XML elements or attributes, do as if the `foo:` prefix was not
here, and everything should work as expected:

    :::xml filename=hello_ns.xml
    <root xmlns:xs="https://example.com/xml/schema">
        <xs:item xs:type="text">Hello, world!</xs:item>
    </root>

<!---->

    :::python
    >>> @xml_handle_element("root", "item")
    ... def handler(node):
    ...     yield (node.attributes["type"], node.text)

    >>> with open("hello_ns.xml", "rb") as f:
    ...    Parser(f).return_from(handler)
    ('text', 'Hello, world!')

## Namespaced elements

If you want to differentiate between XML elements with the same name but different
namespaces, you need to mention namespaces in the handlers using the
[Clark notation](http://www.jclark.com/xml/xmlns.htm).

When parsing an XML element of name `bar` and namespace
`https://example.com/xml/schema`, _BigXML_ looks for a handler in the following order:

1. `{https://example.com/xml/schema}bar`: a handler for the specific namespace
2. `bar`: a handler that does not specify the namespace
3. No handler is used, the element is ignored

!!! Tip

    To match only XML elements of name `bar` that do not have any namespace, use the following: `{}bar`.

Example:

    :::xml filename=colors.xml
    <root
        xmlns="https://example.com/xml/purple"
        xmlns:blue="https://example.com/xml/blue"
        xmlns:red="https://example.com/xml/red">
            <blue:item>Blue</blue:item>
            <item xmlns="https://example.com/xml/blue">Also blue</item>
            <red:item>Red</red:item>
            <item>Purple</item>
    </root>

<!---->

    :::python
    >>> @xml_handle_element("root", "item")
    ... def handler_default(node):
    ...     yield ("default", node.text)

    >>> @xml_handle_element("root", "{}item")
    ... def handler_nothing(node):
    ...     yield ("nothing", node.text)

    >>> @xml_handle_element("root", "{https://example.com/xml/blue}item")
    ... def handler_blue(node):
    ...     yield ("blue", node.text)

    >>> @xml_handle_element("root", "{https://example.com/xml/purple}item")
    ... def handler_purple(node):
    ...     yield ("purple", node.text)

    >>> with open("colors.xml", "rb") as f:
    ...    for item in Parser(f).iter_from(
    ...        handler_default,
    ...        handler_nothing,
    ...        handler_blue,
    ...        handler_purple,
    ...    ):
    ...        print(item)
    ('blue', 'Blue')
    ('blue', 'Also blue')
    ('default', 'Red')
    ('purple', 'Purple')

!!! Note

    In the example above, `handler_purple` is used instead of `handler_nothing` for the item `Purple` because a default namespace has been attached to `<root>` with the attribute `xmlns`.

## Namespaced attributes

When accessing the attributes of a node, you can use one of the following keys:

- `{https://example.com/xml/schema}bar` to get the attribute `bar` with the namespace
  `https://example.com/xml/schema`;
- `{}bar` to get the attribute `bar` without any namespace;
- `bar` to get an attribute `bar` of any namespace.

!!! Warning

    The `bar` syntax always returns the attribute `bar` without any namespace if it exists.

    However, if such an attribute does not exist but several attributes `bar` with
    various namespaces do exist, one of them will be returned. In that case, which
    attribute is returned is not guaranteed, and a warning is emitted accordingly.

Example:

    :::xml filename=attributes_ns.xml
    <root
        xmlns="https://example.com/xml/purple"
        xmlns:blue="https://example.com/xml/blue"
        xmlns:red="https://example.com/xml/red">
            <item color="Green">Case 0</item>
            <item blue:color="Blue">Case 1</item>
            <item red:color="Red">Case 2</item>
            <item color="Green" blue:color="Blue" red:color="Red">Case 3</item>
    </root>

<!---->

    :::python
    >>> @xml_handle_element("root", "item")
    ... def handler(node):
    ...     yield node.text
    ...     yield ("default ns", node.attributes["color"])
    ...     yield ("no ns", node.attributes.get("{}color"))
    ...     yield ("blue ns", node.attributes.get("{https://example.com/xml/blue}color"))

    >>> with open("attributes_ns.xml", "rb") as f:
    ...    for item in Parser(f).iter_from(handler):
    ...        print(item)
    Case 0
    ('default ns', 'Green')
    ('no ns', 'Green')
    ('blue ns', None)
    Case 1
    ('default ns', 'Blue')
    ('no ns', None)
    ('blue ns', 'Blue')
    Case 2
    ('default ns', 'Red')
    ('no ns', None)
    ('blue ns', None)
    Case 3
    ('default ns', 'Green')
    ('no ns', 'Green')
    ('blue ns', 'Blue')

!!! Note

    Contrary to XML elements, no default namespace apply to attributes: in the example,
    `Green` is matched by `{}color` instead of `{https://example.com/xml/purple}color`.
