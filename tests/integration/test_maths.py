from functools import reduce
import operator
from pathlib import Path

from bigxml import Parser, XMLHandler, xml_handle_element, xml_handle_text


def test_maths_eval():
    class Eval(XMLHandler):
        # pylint: disable=no-self-use

        @xml_handle_element("expr")
        def handle_author(self, node):
            yield reduce(
                getattr(operator, node.attributes["op"]),
                node.iter_from(Eval()),
            )

        @xml_handle_text("number")
        def handle_number(self, node):
            yield int(node.text)

    with (Path(__file__).parent / "maths.xml").open("rb") as stream:
        assert list(Parser(stream).iter_from(Eval())) == [1337]
