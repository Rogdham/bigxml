from functools import reduce
import operator
from pathlib import Path

from bigxml import Parser, xml_handle_element, xml_handle_text


def test_maths_eval_list():
    handlers = []

    @xml_handle_element("expr")
    def handle_expr(node):
        yield reduce(
            getattr(operator, node.attributes["op"]),
            node.iter_from(*handlers),
        )

    handlers.append(handle_expr)

    @xml_handle_text("number")
    def handle_number(node):
        yield int(node.text)

    handlers.append(handle_number)

    with (Path(__file__).parent / "maths.xml").open("rb") as stream:
        assert list(Parser(stream).iter_from(*handlers)) == [1337]


def test_maths_eval_class():
    class Eval:
        @staticmethod
        @xml_handle_element("expr")
        def handle_expr(node):
            yield reduce(
                getattr(operator, node.attributes["op"]),
                node.iter_from(Eval),
            )

        @staticmethod
        @xml_handle_text("number")
        def handle_number(node):
            yield int(node.text)

    with (Path(__file__).parent / "maths.xml").open("rb") as stream:
        assert list(Parser(stream).iter_from(Eval)) == [1337]
