from functools import reduce
import operator
from pathlib import Path

from bigxml import Parser, XMLHandler, xml_handle_element, xml_handle_text


def test_maths_eval():
    class Eval(XMLHandler):
        @staticmethod
        @xml_handle_element("expr")
        def handle_expr(node):
            yield reduce(
                getattr(operator, node.attributes["op"]),
                node.iter_from(Eval()),
            )

        @staticmethod
        @xml_handle_text("number")
        def handle_number(node):
            yield int(node.text)

    with (Path(__file__).parent / "maths.xml").open("rb") as stream:
        assert list(Parser(stream).iter_from(Eval())) == [1337]
