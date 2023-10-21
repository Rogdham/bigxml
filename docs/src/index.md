<div class="home-header" markdown="1">

# BigXML

<div class="description">Parse big xml files and stream with&nbsp;ease</div>

</div>

## Introduction

Parsing big XML files in Python is hard. On one hand, regular XML libraries load the
whole file into memory, which will crash the process if the file is too big. Other
solutions such as `iterparse` do read the file as they parse it, but they are complex to
use if you don't want to run out of memory.

This is where the _BigXML_ library shines:

- Works with XML files of any size
- No need to do memory management yourself
- Pythonic API (using decorators similar to what _Flask_ does)
- Any stream can easily be parsed, not just files (e.g.
  [usage with _Requests_](recipes.md#requests))
- Secure from usual attacks against XML parsers

## Philosophy

Because it needs to be able to handle big files, _BigXML_ parses the input streams in on
pass. This means that once an XML element has been seen, you cannot go back to it. In
other words, all computations for a node need to be performed when it is encountered.

This library borrows ideas from event-based programming. Conceptually, you can define
handlers that will react to XML elements with specific names. _BigXML_ will then
dispatch the nodes of the stream being parsed to the good handlers.

As the XML document is parsed, handlers of deeper nodes may yield some piece of
information that will be gathered by parent handlers. At the end of the day, this
produces a single iterable that will be handled by your application.

!!! Tip

    Think big and never go backward, or you will get
    [an exception](faq.md#exnodes-out-of-order-exception).

## Installation

Install _BigXML_ with pip:

    :::sh
    $ python -m pip install bigxml

## Imports

The most used imports are the following:

    :::python
    from bigxml import Parser, xml_handle_element, xml_handle_text

If you want to catch [exceptions](exceptions.md) raised by this module:

    :::python
    from bigxml import BigXmlError

For [type hints](typing.md), you may also import:

    :::python
    from bigxml import HandlerTypeHelper, Streamable, XMLElement, XMLElementAttributes, XMLText

!!! Warning

    Always import directly from `bigxml`. Importing from submodules is unsupported.
