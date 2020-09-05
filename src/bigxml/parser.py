from defusedxml.ElementTree import iterparse

from bigxml.handle_mgr import HandleMgr
from bigxml.nodes import XMLElement, XMLText
from bigxml.utils import IterWithRollback


def _parse(iterator, handler, parents, parent_elem, expected_iteration):
    if iterator.iteration != expected_iteration:
        raise RuntimeError("Tried to access a node out of order")

    depth = 0
    last_child = None

    def handle_text():
        if last_child is not None:
            text = last_child.tail
        elif parent_elem is not None:
            text = parent_elem.text
        else:
            text = None
        if text:
            node = XMLText(text=text, parents=parents)
            yield from handler(node)

    def create_node(elem, iteration):
        node = XMLElement(name=elem.tag, attributes=elem.attrib, parents=parents)
        node.set_handle(
            lambda h: _parse(iterator, h, parents + (node,), elem, iteration)
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
    def __init__(self, stream):
        self.stream = stream
        iterator = IterWithRollback(iterparse(stream, ("start", "end")))
        self.set_handle(lambda h: _parse(iterator, h, (), None, 0))
