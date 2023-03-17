from dataclasses import dataclass
import sys
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Optional, Tuple, Union

from bigxml import (
    HandlerTypeHelper,
    Parser,
    XMLElement,
    XMLText,
    xml_handle_element,
    xml_handle_text,
)

if sys.version_info < (3, 11):
    from typing import NoReturn as Never
else:
    from typing import Never

if TYPE_CHECKING:
    from typing_extensions import assert_type
else:

    def assert_type(val: Any, _: Any) -> Any:  # noqa: ANN401
        return val


# Note: the aim of this file is to test the typing of return-values
# for iter_from and return_from as they would be used in the wild.
# As a result, we don't try to factor code or do anything smart here.


XML = b"""
<root>
    <item>one</item>
    <item>two</item>
    <item>three</item>
</root>
"""

# no handlers


def test_no_handlers() -> None:
    iterator = Parser(XML).iter_from()
    assert_type(iterator, Iterator[Never])
    assert not list(iterator)

    value = Parser(XML).return_from()
    assert_type(value, None)
    assert value is None


# function


def catchall(node: Union[XMLElement, XMLText]) -> Iterator[int]:
    yield len(node.text)


@xml_handle_element("root", "item")
def element_handler(node: XMLElement) -> Iterator[str]:
    yield node.text


@xml_handle_text("root")
def text_handler(node: XMLText) -> Iterator[int]:
    yield len(node.text)


def test_catchall() -> None:
    iterator = Parser(XML).iter_from(catchall)
    assert_type(iterator, Iterator[int])
    assert list(iterator) == [11]

    value = Parser(XML).return_from(catchall)
    assert_type(value, Optional[int])
    assert value == 11


def test_element_handler() -> None:
    iterator = Parser(XML).iter_from(element_handler)
    assert_type(iterator, Iterator[str])
    assert list(iterator) == ["one", "two", "three"]

    value = Parser(XML).return_from(element_handler)
    assert_type(value, Optional[str])
    assert value == "three"


def test_text_handler() -> None:
    iterator = Parser(XML).iter_from(text_handler)
    assert_type(iterator, Iterator[int])
    assert list(iterator) == [5, 5, 5, 1]

    value = Parser(XML).return_from(text_handler)
    assert_type(value, Optional[int])
    assert value == 1


# class


class Nothing:
    pass


class HoldNode:
    def __init__(self, node: XMLElement) -> None:
        self.name = node.name
        self.text = node.text


@xml_handle_element("root", "item")
class ItemHoldNode:
    def __init__(self, node: XMLElement) -> None:
        self.name = node.name
        self.text = node.text


@dataclass
class WithSubHandler:
    data: str = ""

    @xml_handle_text("root", "item")
    def text_handler(self, node: XMLText) -> None:
        self.data += f"<{node.text}>"


class WithCustomHandler:
    def __init__(self) -> None:
        self.count = 0

    @xml_handle_text("root", "item")
    def text_handler(self, node: XMLText) -> Iterable[Tuple[int, str]]:
        yield self.count, node.text
        self.count += 1

    def xml_handler(self, iterable: Iterable[Tuple[int, str]]) -> Iterable[str]:
        for count, text in iterable:
            yield f"item {count} -> {text}"
        yield f"total -> {self.count}"


def test_class_nothing() -> None:
    iterator = Parser(XML).iter_from(Nothing)
    assert_type(iterator, Iterator[Nothing])
    items = list(iterator)
    assert len(items) == 1
    assert isinstance(items[0], Nothing)

    value = Parser(XML).return_from(Nothing)
    assert_type(value, Optional[Nothing])
    assert isinstance(value, Nothing)


def test_class_init() -> None:
    iterator = Parser(XML).iter_from(HoldNode)
    assert_type(iterator, Iterator[HoldNode])
    items = list(iterator)
    assert len(items) == 1
    assert isinstance(items[0], HoldNode)
    assert items[0].name == "root"
    assert items[0].text == "onetwothree"

    value = Parser(XML).return_from(HoldNode)
    assert_type(value, Optional[HoldNode])
    assert isinstance(value, HoldNode)
    assert value.name == "root"
    assert value.text == "onetwothree"


def test_class_item_init() -> None:
    iterator = Parser(XML).iter_from(ItemHoldNode)
    assert_type(iterator, Iterator[ItemHoldNode])
    items = list(iterator)
    assert len(items) == 3
    assert all(isinstance(item, ItemHoldNode) for item in items)
    assert all(item.name == "item" for item in items)
    assert [item.text for item in items] == ["one", "two", "three"]

    value = Parser(XML).return_from(ItemHoldNode)
    assert_type(value, Optional[ItemHoldNode])
    assert isinstance(value, ItemHoldNode)
    assert value.name == "item"
    assert value.text == "three"


def test_class_with_subhandler() -> None:
    iterator = Parser(XML).iter_from(WithSubHandler)
    assert_type(iterator, Iterator[WithSubHandler])
    items = list(iterator)
    assert items == [WithSubHandler("<one><two><three>")]

    value = Parser(XML).return_from(WithSubHandler)
    assert_type(value, Optional[WithSubHandler])
    assert value == WithSubHandler("<one><two><three>")


def test_class_with_custom_handler() -> None:
    iterator = Parser(XML).iter_from(WithCustomHandler)
    assert_type(iterator, Iterator[str])
    items = list(iterator)
    assert items == [
        "item 0 -> one",
        "item 1 -> two",
        "item 2 -> three",
        "total -> 3",
    ]

    value = Parser(XML).return_from(WithCustomHandler)
    assert_type(value, Optional[str])
    assert value == "total -> 3"


# instance


@xml_handle_element("root")
class SubHandler:
    @xml_handle_text("item")
    def text_handler(self, node: XMLText) -> Iterator[int]:
        yield len(node.text)


def test_instance_subhandler() -> None:
    iterator = Parser(XML).iter_from(SubHandler())
    assert_type(iterator, Iterator[object])
    items = list(iterator)
    assert items == [3, 3, 5]

    value = Parser(XML).return_from(SubHandler())
    assert_type(value, Optional[object])
    assert value == 5


# syntactic sugar


def test_syntactic_sugar_tuple() -> None:
    iterator = Parser(XML).iter_from(("root", "item"))
    assert_type(iterator, Iterator[XMLElement])
    assert [node.text for node in iterator] == ["one", "two", "three"]

    value = Parser(XML).return_from(("root", "item"))
    assert_type(value, Optional[XMLElement])
    assert value
    # cannot get node.text as it is consumed at that point
    assert isinstance(value, XMLElement)
    assert value.name == "item"


def test_syntactic_sugar_list() -> None:
    iterator = Parser(XML).iter_from(["root", "item"])
    assert_type(iterator, Iterator[XMLElement])
    assert [node.text for node in iterator] == ["one", "two", "three"]

    value = Parser(XML).return_from(["root", "item"])
    assert_type(value, Optional[XMLElement])
    assert value
    # cannot get node.text as it is consumed at that point
    assert isinstance(value, XMLElement)
    assert value.name == "item"


def test_syntactic_sugar_str() -> None:
    iterator = Parser(XML).iter_from("root")
    assert_type(iterator, Iterator[XMLElement])
    assert [node.text for node in iterator] == ["onetwothree"]

    value = Parser(XML).return_from("root")
    assert_type(value, Optional[XMLElement])
    assert value
    # cannot get node.text as it is consumed at that point
    assert isinstance(value, XMLElement)
    assert value.name == "root"


# mixed


def test_mixed_iterator_types() -> None:
    iterator = Parser(XML).iter_from(
        HandlerTypeHelper[Union[str, int]],  # little help
        element_handler,
        text_handler,
    )
    assert_type(iterator, Iterator[Union[str, int]])
    assert list(iterator) == [5, "one", 5, "two", 5, "three", 1]

    value = Parser(XML).return_from(
        HandlerTypeHelper[Union[str, int]],  # little help
        element_handler,
        text_handler,
    )
    assert_type(value, Optional[Union[str, int]])
    assert value == 1


def test_mixed_syntactic_sugar() -> None:
    iterator = Parser(XML).iter_from(("root", "item"), text_handler)
    assert_type(iterator, Iterator[Union[XMLElement, int]])
    assert [
        item.name if isinstance(item, XMLElement) else item for item in iterator
    ] == [5, "item", 5, "item", 5, "item", 1]

    value = Parser(XML).return_from(("root", "item"), text_handler)
    assert_type(value, Optional[Union[XMLElement, int]])
    assert value == 1


def test_mixed_callable_class() -> None:
    @xml_handle_element("root", "item")
    @dataclass
    class WithSubHandler2:
        data: str = ""

        @xml_handle_text
        def text_handler(self, node: XMLText) -> None:
            self.data += f"<{node.text}>"

    @xml_handle_text("root")
    def text_handler2(node: XMLText) -> Iterator[WithSubHandler2]:
        yield WithSubHandler2(f"~{node.text}~")

    iterator = Parser(XML).iter_from(text_handler2, WithSubHandler2)
    assert_type(iterator, Iterator[WithSubHandler2])
    items = list(iterator)
    assert items == [
        WithSubHandler2("~\n    ~"),
        WithSubHandler2("<one>"),
        WithSubHandler2("~\n    ~"),
        WithSubHandler2("<two>"),
        WithSubHandler2("~\n    ~"),
        WithSubHandler2("<three>"),
        WithSubHandler2("~\n~"),
    ]

    value = Parser(XML).return_from(text_handler2, WithSubHandler2)
    assert_type(value, Optional[WithSubHandler2])
    assert value == WithSubHandler2("~\n~")
