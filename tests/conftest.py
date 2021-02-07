from pathlib import Path
import sys

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        dirname = Path(item.fspath).parent.name
        item.add_marker(getattr(pytest.mark, dirname))


# skipping some files due to syntax not yet supported
collect_ignore = []
if sys.version_info < (3, 8):
    collect_ignore.append("unit/test_utils_get_mandatory_params.py")  # PEP 570
