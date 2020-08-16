from dataclasses import dataclass
from typing import Dict, Tuple

from bigxml.handle_mgr import HandleMgr
from bigxml.utils import extract_namespace_name


@dataclass
class XMLElement(HandleMgr):
    name: str
    attributes: Dict[str, str]
    parents: Tuple["XMLElement"]
    namespace: str = None

    def __post_init__(self):
        if not self.namespace:
            self.namespace, self.name = extract_namespace_name(self.name)


@dataclass
class XMLText:
    text: str
    parents: Tuple["XMLElement"]

    # classname attribute name to be easily switched on with XMLElement
    name = "\0text"  # \0 makes sure it is an invalid element name
