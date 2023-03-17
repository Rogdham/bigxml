# pylint: disable=unused-argument
# ruff: noqa: ARG001

from typing import Callable, List, Tuple

import pytest

from bigxml.utils import get_mandatory_params


def fct0():  # type: ignore[no-untyped-def] # noqa: ANN201
    pass  # for tests


def fct1(arg0):  # type: ignore[no-untyped-def] # noqa: ANN001,ANN201
    pass  # for tests


def fct2(arg0, arg1, arg2):  # type: ignore[no-untyped-def] # noqa: ANN001,ANN201
    pass  # for tests


def fct3(arg0=13, arg1=37, arg2=42):  # type: ignore[no-untyped-def] # noqa: ANN001,ANN201
    pass  # for tests


def fct4(arg0, /, arg1, *, arg2, arg3=3):  # type: ignore[no-untyped-def] # noqa: ANN001,ANN201
    pass  # for tests


# pylint: disable-next=line-too-long
def fct5(arg0, /, arg1, *arg2, arg3, arg4=4, **arg5):  # type: ignore[no-untyped-def] # noqa: ANN001,ANN002,ANN003,ANN201
    pass  # for tests


def fct6(
    arg0: int,
    /,
    arg1: int,
    *arg2: List[int],
    arg3: int,
    arg4: int = 4,
    **arg5: List[int],
) -> None:
    pass  # for tests


# pylint: enable=unused-argument


@pytest.mark.parametrize(
    ["fct", "expected"],
    [
        (fct0, ()),
        (fct1, ("arg0",)),
        (fct2, ("arg0", "arg1", "arg2")),
        (fct3, ()),
        (fct4, ("arg0", "arg1", "arg2")),
        (fct5, ("arg0", "arg1", "arg3")),
        (fct6, ("arg0", "arg1", "arg3")),
        (int, ()),
        (dict, ()),
    ],
    ids=lambda x: str(x.__name__ if callable(x) else x),
)  # type: ignore[misc]
# Typing note: see https://github.com/python/mypy/issues/13436
def test_mandatory_params(
    fct: Callable[..., object], expected: Tuple[str, ...]
) -> None:
    assert get_mandatory_params(fct) == expected
