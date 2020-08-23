from pathlib import Path

from bigxml import XMLHandler, parse, xml_handle_element


def test_maths_eval():
    class Handler(XMLHandler):
        # pylint: disable=no-self-use

        @xml_handle_element("comments", "comment")
        def handle_author(self, node):
            yield node.text

    with (Path(__file__).parent / "comments.xml").open("rb") as f_in:
        items = parse(f_in, Handler())
        assert next(items) == "Test"
        assert next(items) == "Hello everyone!"
        assert next(items) == (
            "I've found this quote that I feel you may like: "
            "The grass is greener where you water it. "
            "—Neil Barringham "
            "Feel free to share it!"
        )
