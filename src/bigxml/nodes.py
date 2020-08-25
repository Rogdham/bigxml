from dataclasses import dataclass
from typing import Dict, Tuple

from bigxml.handle_mgr import HandleMgr
from bigxml.utils import extract_namespace_name


def _handler_get_text(node):
    if isinstance(node, XMLText):
        yield node.text
    elif isinstance(node, XMLElement):
        yield from node.iter_from(_handler_get_text)
    else:  # pragma: no cover
        raise RuntimeError  # should not happen


@dataclass
class XMLElement(HandleMgr):
    name: str
    attributes: Dict[str, str]
    parents: Tuple["XMLElement"]
    namespace: str = None

    def __post_init__(self):
        if not self.namespace:
            self.namespace, self.name = extract_namespace_name(self.name)

    @property
    def text(self):
        output = ""
        last_ends_with_space = False
        for text in self.iter_from(_handler_get_text):
            if not text:
                continue
            text_stripped = text.strip()
            if (last_ends_with_space or not text.startswith(text_stripped)) and output:
                output += " "
            output += text_stripped
            last_ends_with_space = not text.endswith(text_stripped)
        return output


@dataclass
class XMLText:
    text: str
    parents: Tuple["XMLElement"]

    # classname attribute name to be easily switched on with XMLElement
    name = "\0text"  # \0 makes sure it is an invalid element name
