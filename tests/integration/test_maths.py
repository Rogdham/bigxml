from functools import reduce
import operator
from typing import Callable, Iterable, Iterator, List, Optional, Union

from bigxml import Parser, XMLElement, XMLText, xml_handle_element, xml_handle_text

XML = b"""
<expr op="sub">
    <expr op="mul">
        <number>42</number>
        <expr op="add">
            <number>13</number>
            <number>25</number>
        </expr>
    </expr>
    <number>7</number>
    <expr op="mul">
        <expr op="add">
            <number>1</number>
            <number>3</number>
            <number>3</number>
            <number>7</number>
        </expr>
        <number>18</number>
    </expr>
</expr>
"""


def test_maths_eval_list() -> None:
    handlers: List[Callable[[Union[XMLElement, XMLText]], Optional[Iterable[int]]]] = []

    @xml_handle_element("expr")
    def handle_expr(node: XMLElement) -> Iterator[int]:
        yield reduce(
            getattr(operator, node.attributes["op"]),
            node.iter_from(*handlers),
        )

    handlers.append(handle_expr)

    @xml_handle_text("number")
    def handle_number(node: XMLText) -> Iterator[int]:
        yield int(node.text)

    handlers.append(handle_number)

    assert list(Parser(XML).iter_from(*handlers)) == [1337]


def test_maths_eval_class() -> None:
    class Eval:
        @staticmethod
        @xml_handle_element("expr")
        def handle_expr(node: XMLElement) -> Iterator[int]:
            yield reduce(
                getattr(operator, node.attributes["op"]),
                node.iter_from(Eval),
            )

        @staticmethod
        @xml_handle_text("number")
        def handle_number(node: XMLText) -> Iterator[int]:
            yield int(node.text)

        @staticmethod
        def xml_handler(generator: Iterator[int]) -> Iterator[int]:
            yield from generator

    assert list(Parser(XML).iter_from(Eval)) == [1337]
