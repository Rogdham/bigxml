# Decorators

The `xml_handle_element` and `xml_handle_text` functions can be used to decorate
functions or classes [handlers](handlers.md).

They differ in the type of node to handle:

- `xml_handle_element` is for XML elements, and passes an
  [`XMLElement` instance](nodes.md#xmlelement) to the decorated function;
- `xml_handle_text` is for character data (i.e. text), and passes an
  [`XMLText` instance](nodes.md#xmltext) to the decorated function.

<!---->

    :::xml filename=paragraph.xml
    <p>
        Hello,
        <em>
            world
        </em>
        !
    </p>

<!---->

    :::python
    >>> @xml_handle_text("p")
    ... def handle_text(node):
    ...     yield ("text", type(node).__name__, node.text)

    >>> @xml_handle_element("p", "em")
    ... def handle_em(node):
    ...     yield ("em", type(node).__name__, node.text)

    >>> with open("paragraph.xml", "rb") as f:
    ...    for item in Parser(f).iter_from(handle_text, handle_em):
    ...        print(item)
    ('text', 'XMLText', '\n    Hello,\n    ')
    ('em', 'XMLElement', 'world')
    ('text', 'XMLText', '\n    !\n')

As you can see, no special treatment is applied to the text of `XMLText` items, whereas
accessing the `text` property of an `XMLElement instance` tries to strip unnecessary
spaces.

Note that `@xml_handle_text` is a shortcut for `@xml_handle_text()`:

    :::python
    >>> @xml_handle_element("p")
    ... class Handler(list):
    ...     @xml_handle_text
    ...     def handle_text(self, node):
    ...         self.append(node.text)

    >>> with open("paragraph.xml", "rb") as f:
    ...    Parser(f).return_from(Handler)
    ['\n    Hello,\n    ', '\n    !\n']
