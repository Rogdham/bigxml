from pathlib import Path

from bigxml import Parser, xml_handle_element


def test_comments():
    @xml_handle_element("comments", "comment")
    def handler(node):
        yield node.text

    with (Path(__file__).parent / "comments.xml").open("rb") as stream:
        items = Parser(stream).iter_from(handler)
        assert next(items) == "Test"
        assert next(items) == "Hello everyone!"
        assert next(items) == (
            "I've found this quote that I feel you may like: "
            "The grass is greener where you water it. "
            "—Neil Barringham "
            "Feel free to share it!"
        )
