from typing import TYPE_CHECKING, Callable, Iterator, Optional, Tuple, Union
import warnings

from defusedxml.ElementTree import iterparse

from bigxml.exceptions import rewrite_exceptions
from bigxml.handle_mgr import HandleMgr
from bigxml.nodes import XMLElement, XMLElementAttributes, XMLText
from bigxml.stream import StreamChain
from bigxml.typing import Streamable, T
from bigxml.utils import IterWithRollback

if TYPE_CHECKING:
    from defusedxml.ElementTree import Element


def _parse(
    iterator: IterWithRollback[Tuple[str, "Element"]],
    handler: Callable[[Union[XMLElement, XMLText]], Iterator[T]],
    parents: Tuple[XMLElement, ...],
    parent_elem: Optional["Element"],
    expected_iteration: int,
) -> Iterator[T]:
    if iterator.iteration != expected_iteration:
        raise RuntimeError("Tried to access a node out of order")

    depth = 0
    last_child: Optional["Element"] = None

    def handle_text() -> Iterator[T]:
        if last_child is not None:
            text = last_child.tail
        elif parent_elem is not None:
            text = parent_elem.text
        else:
            text = None
        if text:
            node = XMLText(text=text, parents=parents)
            yield from handler(node)

    def create_node(elem: "Element", iteration: int) -> Union[XMLElement, XMLText]:
        node = XMLElement(
            name=elem.tag, attributes=XMLElementAttributes(elem.attrib), parents=parents
        )
        # pylint: disable=protected-access
        node._handle = lambda h: _parse(  # noqa: SLF001
            iterator, h, (*parents, node), elem, iteration
        )
        return node

    for action, elem in iterator:
        if action == "start":
            if depth == 0:
                yield from handle_text()
                yield from handler(create_node(elem, iterator.iteration))

            depth += 1

        elif action == "end":
            depth -= 1

            if depth < 0:
                yield from handle_text()
                iterator.rollback()  # parent needs to see end tag
                return

            if last_child is not None:
                last_child.clear()

            last_child = elem

        else:  # pragma: no cover
            raise RuntimeError  # should not happen


class Parser(HandleMgr):
    def __init__(
        self,
        *streams: Streamable,
        insecurely_allow_entities: bool = False,
    ) -> None:
        if insecurely_allow_entities:
            warnings.warn(
                "Using 'insecurely_allow_entities' makes your code vulnerable to some XML attacks."
                " Are you sure you trust where the input streams are coming from?",
                UserWarning,
                stacklevel=1,
            )
        iterator = IterWithRollback(
            rewrite_exceptions(
                iterparse(
                    StreamChain(*streams),
                    ("start", "end"),
                    forbid_entities=not insecurely_allow_entities,
                )
            )
        )
        self._handle = lambda h: _parse(iterator, h, (), None, 0)
