from typing import Iterator

from bigxml import Parser, XMLElement, xml_handle_element

XML = b"""
<comments>
    <comment>Test</comment>
    <comment>
        <p>Hello everyone!</p>
    </comment>
    <comment>
        I've found this quote that I feel you may like:
        <blockquote cite="https://www.osmquote.com/quote/neil-barringham-quote-54c4b8">
            The grass is greener where you water it.
            <footer>-Neil Barringham</footer>
        </blockquote>
        Feel free to share it!
    </comment>
</comments>
"""


def test_comments() -> None:
    @xml_handle_element("comments", "comment")
    def handler(node: XMLElement) -> Iterator[str]:
        yield node.text

    items = Parser(XML).iter_from(handler)
    assert next(items) == "Test"
    assert next(items) == "Hello everyone!"
    assert next(items) == (
        "I've found this quote that I feel you may like:"
        " The grass is greener where you water it."
        " -Neil Barringham"
        " Feel free to share it!"
    )
