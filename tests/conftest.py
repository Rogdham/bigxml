from pathlib import Path
from typing import List

import pytest


def pytest_collection_modifyitems(
    # pylint: disable=unused-argument
    config: pytest.Config,  # noqa: ARG001
    items: List[pytest.Item],
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
