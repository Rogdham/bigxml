from pathlib import Path
import sys
from typing import TYPE_CHECKING, List

import pytest

if TYPE_CHECKING:
    # see https://github.com/pytest-dev/pytest/issues/7469
    # for pytest exporting from pytest and not _pytest
    from _pytest.config import Config
    from _pytest.nodes import Item


def pytest_collection_modifyitems(
    # pylint: disable=unused-argument
    config: "Config",
    items: List["Item"],
) -> None:
    root = Path(__file__).parent.parent
    for item in items:
        relative = Path(item.fspath).parent.relative_to(root)
        if relative.parent.name == "docs":
            mark = "docs"
        elif relative.parent.name == "tests":
            mark = relative.name
        else:
            raise NotImplementedError
        item.add_marker(getattr(pytest.mark, mark))


# skipping some files due to syntax not yet supported
collect_ignore: List[str] = []
if sys.version_info < (3, 8):
    collect_ignore.append("unit/test_utils_get_mandatory_params.py")  # PEP 570
