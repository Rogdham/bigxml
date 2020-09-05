from pathlib import Path

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        dirname = Path(item.fspath).parent.name
        item.add_marker(getattr(pytest.mark, dirname))
