from os import chdir, getcwd
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Dict, Iterator
from unittest.mock import Mock

import pytest

from bigxml import (
    HandlerTypeHelper,
    Parser,
    XMLElement,
    XMLText,
    xml_handle_element,
    xml_handle_text,
)


@pytest.fixture(scope="module", autouse=True)
def _import_pytest(doctest_namespace: Dict[str, object]) -> None:
    doctest_namespace["HandlerTypeHelper"] = HandlerTypeHelper
    doctest_namespace["Parser"] = Parser
    doctest_namespace["XMLElement"] = XMLElement
    doctest_namespace["XMLText"] = XMLText
    doctest_namespace["xml_handle_element"] = xml_handle_element
    doctest_namespace["xml_handle_text"] = xml_handle_text

    requests = Mock()
    requests_response = requests.get.return_value
    requests_response.iter_content.return_value = iter(
        (
            b"<root>",
            b"<item>This example shows parsing in streaming with Requests.</item>",
            b"<item>It works quite well!</item>",
            b"</root>",
        )
    )
    doctest_namespace["requests"] = requests


@pytest.fixture(scope="module", autouse=True)
def _create_files() -> Iterator[None]:
    cwd = getcwd()
    docs_path = Path(__file__).parent
    try:
        with TemporaryDirectory() as dirname:
            chdir(dirname)
            for md_path in docs_path.glob("**/*.md"):
                for match in re.finditer(
                    "    :::xml filename=(.*?)((?:\n    .*)+)",
                    md_path.read_text(),
                ):
                    groups = match.groups()
                    filename = groups[0].strip()
                    content = groups[1].replace("\n    ", "\n")[1:]
                    path = Path(dirname) / filename.strip()
                    if path.exists() and path.read_text() != content:
                        raise ValueError(f"File already exists: {filename}")
                    path.write_text(content)

            yield
    finally:
        chdir(cwd)
