from defusedxml.ElementTree import iterparse

from bigxml.elements import XMLElement, XMLText
from bigxml.utils import IterWithRollback


def _parse(iterator, handler, parents=(), parent_elem=None):
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

    def create_node(elem, parents):
        node = XMLElement(name=elem.tag, attributes=elem.attrib, parents=parents)
        node.set_handle(lambda h: _parse(iterator, h, parents + (node,), elem,))
        return node

    for action, elem in iterator:
        if action == "start":
            if depth == 0:
                yield from handle_text()
                yield from handler(create_node(elem, parents))

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


def parse(f_in, handler):
    iterator = IterWithRollback(iterparse(f_in, ("start", "end")))
    return _parse(iterator, handler)
