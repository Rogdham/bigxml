# Quickstart

Let's get started by parsing the [atom feed] of the [XKCD comic][xkcd atom], which
should look similar to the following (some small modifications have been made for
demonstration purposes):

    :::xml filename=atom.xml
    <?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="https://www.w3.org/2005/Atom" xml:lang="en">
        <title>xkcd.com</title>
        <link href="https://xkcd.com/" rel="alternate"></link>
        <id>https://xkcd.com/</id>
        <updated>2021-03-19T00:00:00Z</updated>
        <entry>
            <title>Solar System Cartogram</title>
            <link href="https://xkcd.com/2439/" rel="alternate"></link>
            <updated>2021-03-19T00:00:00Z</updated>
            <id>2439</id>
        </entry>
        <entry>
            <title>Siri</title>
            <link href="https://xkcd.com/2438/" rel="alternate"></link>
            <updated>2021-03-17T00:00:00Z</updated>
            <id>2438</id>
        </entry>
        <entry>
            <title>Post-Vaccine Party</title>
            <link href="https://xkcd.com/2437/" rel="alternate"></link>
            <updated>2021-03-15T00:00:00Z</updated>
            <id>2437</id>
        </entry>
        <entry>
            <title>Circles</title>
            <link href="https://xkcd.com/2436/" rel="alternate"></link>
            <updated>2021-03-12T00:00:00Z</updated>
            <id>2436</id>
        </entry>
    </feed>

[atom feed]: https://en.wikipedia.org/wiki/Atom_(Web_standard)
[xkcd atom]: https://xkcd.com/atom.xml

For this tutorial, save that into an `atom.xml` file (we will learn to parse HTTP
responses in streaming later). Make sure you have
[_BigXML_ installed](index.md#installation) so that you can follow along.

## Getting nodes and data

Say we want to get the comics' titles. To do so, we will create a handler function. We
pass the path to the `title` XML elements we are interested in as arguments of the
`xml_handle_element` decorator:

    :::python
    >>> @xml_handle_element("feed", "entry", "title")
    ... def handler(node):
    ...     yield node.text  # node content as a str

Next, we need to instantiate a `Parser` with a stream. In our case, we have the atom
feed saved into a file, so we pass the file object.

Finally, we call `iter_from` to obtain an iterator that will get though all the items
yielded by the handler:

    :::python
    >>> with open("atom.xml", "rb") as f:
    ...     for item in Parser(f).iter_from(handler):
    ...         print(item)
    Solar System Cartogram
    Siri
    Post-Vaccine Party
    Circles

## Accessing attributes

Now, we will get the links to the comics. This time, we are interested in the value of
the `href` attribute of the `link` elements:

    :::python
    >>> @xml_handle_element("feed", "entry", "link")
    ... def handler(node):
    ...     yield node.attributes["href"]

The rest of the code works as you would expect:

    :::python
    >>> with open("atom.xml", "rb") as f:
    ...     for item in Parser(f).iter_from(handler):
    ...         print(item)
    https://xkcd.com/2439/
    https://xkcd.com/2438/
    https://xkcd.com/2437/
    https://xkcd.com/2436/

## Combining handlers

But what if we want both titles and links?

We can do the following:

- Create handlers for `title` and `link` children of an `entry` element;
- Call those two handlers from a third handler that takes care of `entry` elements.

<!---->

    :::python
    >>> @xml_handle_element("title")
    ... def handle_title(node):
    ...     yield node.text

    >>> @xml_handle_element("link")
    ... def handle_link(node):
    ...     yield node.attributes["href"]

    >>> @xml_handle_element("feed", "entry")
    ... def handle_entry(node):
    ...     yield 'new entry'
    ...     yield from node.iter_from(handle_title, handle_link)

!!! Note

    The `xml_handle_element` decorators for `handle_title` and `handle_link` use a path
    starting from the `entry` element, since these handlers are passed to the
    `iter_from` method of an `entry` node.

<!---->

    :::python
    >>> with open("atom.xml", "rb") as f:
    ...     for item in Parser(f).iter_from(handle_entry):
    ...         print(item)
    new entry
    Solar System Cartogram
    https://xkcd.com/2439/
    new entry
    Siri
    https://xkcd.com/2438/
    new entry
    Post-Vaccine Party
    https://xkcd.com/2437/
    new entry
    Circles
    https://xkcd.com/2436/

We are not really satisfied with the result: it is not really possible to differentiate
between titles and links of comics, because all we get from calling
`Parser(f).iter_from(handle_entry)` are strings. Also, it is not easy to see which link
is for which title.

Ideally, we would like to group each entry into an object to be able to work on it.
Using [dataclasses][dataclass] is a natural development:

[dataclass]: https://docs.python.org/3/library/dataclasses.html

    :::python
    >>> from dataclasses import dataclass

    >>> @xml_handle_element("feed", "entry")
    ... @dataclass
    ... class Entry:
    ...     title: str = 'N/A'
    ...     link: str = 'N/A'
    ...
    ...     @xml_handle_element("title")
    ...     def handle_title(self, node):
    ...         self.title = node.text
    ...
    ...     @xml_handle_element("link")
    ...     def handle_link(self, node):
    ...         self.link = node.attributes["href"]

    >>> with open("atom.xml", "rb") as f:
    ...     for item in Parser(f).iter_from(Entry):
    ...         print(item)
    Entry(title='Solar System Cartogram', link='https://xkcd.com/2439/')
    Entry(title='Siri', link='https://xkcd.com/2438/')
    Entry(title='Post-Vaccine Party', link='https://xkcd.com/2437/')
    Entry(title='Circles', link='https://xkcd.com/2436/')
