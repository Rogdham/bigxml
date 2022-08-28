from dataclasses import dataclass
import sys
from typing import Dict, Iterator, Tuple, Union
import warnings

from bigxml.handle_mgr import HandleMgr
from bigxml.utils import extract_namespace_name

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Mapping
else:  # pragma: no cover
    from collections.abc import Mapping


class XMLElementAttributes(Mapping[str, str]):
    def __init__(self, attributes: Mapping[str, str]) -> None:
        self._items: Dict[str, Tuple[int, str]] = {}  # key -> (alternatives, value)
        self._len = 0
        for key, value in attributes.items():
            namespace, name = extract_namespace_name(key)
            self._items[f"{{{namespace}}}{name}"] = (-1, value)
            self._len += 1
            if namespace:
                alternatives, value = self._items.get(name, (0, value))
                if alternatives != -1:
                    self._items[name] = (alternatives + 1, value)
            else:
                self._items[name] = (-1, value)

    def __getitem__(self, key: str) -> str:
        alternatives, value = self._items[key]
        if alternatives > 1:
            warnings.warn(
                (
                    f"Several alternatives for attribute name '{key}'."
                    f" Specify namespace by using '{{namespace}}{key}' as the key."
                ),
                RuntimeWarning,
            )
        return value

    def __iter__(self) -> Iterator[str]:
        for key, value in self._items.items():
            if key.startswith("{") and value[0] == -1:
                if key.startswith("{}"):
                    yield key[2:]
                else:
                    yield key

    def __len__(self) -> int:
        return self._len

    def __repr__(self) -> str:
        return f"XMLElementAttributes({self})"

    def __str__(self) -> str:
        return str(dict(self))


def _handler_get_text(node: Union["XMLElement", "XMLText"]) -> Iterator[str]:
    if isinstance(node, XMLText):
        yield node.text
    elif isinstance(node, XMLElement):
        yield from node.iter_from(_handler_get_text)
    else:  # pragma: no cover
        raise RuntimeError  # should not happen


@dataclass
class XMLElement(HandleMgr):
    name: str
    attributes: XMLElementAttributes
    parents: Tuple["XMLElement", ...]
    namespace: str = ""

    def __post_init__(self) -> None:
        if not self.namespace:
            self.namespace, self.name = extract_namespace_name(self.name)

    def __str__(self) -> str:
        parts = []
        if self.namespace:
            parts.append(f"{{{self.namespace}}}{self.name}")
        else:
            parts.append(self.name)
        if self.attributes:
            parts.append(f"attributes={self.attributes}")
        if self.parents:
            parts.append(f"parents={'>'.join(node.name for node in self.parents)}")
        return f"XMLElement({', '.join(parts)})"

    @property
    def text(self) -> str:
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
    parents: Tuple[XMLElement, ...]

    # classname attribute name to be easily switched on with XMLElement
    name = "\0text"  # \0 makes sure it is an invalid element name

    def __str__(self) -> str:
        parts = [repr(self.text)]
        if self.parents:
            parts.append(f"parents={'>'.join(node.name for node in self.parents)}")
        return f"XMLText({', '.join(parts)})"
