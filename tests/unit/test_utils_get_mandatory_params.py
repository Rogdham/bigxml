# pylint: disable=unused-argument
# ruff: noqa: ARG001

from functools import partial
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
        pytest.param(fct0, (), id="fct0"),
        pytest.param(fct1, ("arg0",), id="fct1"),
        pytest.param(fct2, ("arg0", "arg1", "arg2"), id="fct2"),
        pytest.param(fct3, (), id="fct3"),
        pytest.param(fct4, ("arg0", "arg1", "arg2"), id="fct4"),
        pytest.param(fct5, ("arg0", "arg1", "arg3"), id="fct5"),
        pytest.param(fct6, ("arg0", "arg1", "arg3"), id="fct6"),
        pytest.param(partial(fct1, 42), (), id="partial-fct1"),
        pytest.param(partial(fct2, 13, 37), ("arg2",), id="partial-fct2"),
        pytest.param(int, (), id="int"),
        pytest.param(dict, (), id="dict"),
    ],
)  # type: ignore[misc]
# Typing note: see https://github.com/python/mypy/issues/13436
def test_mandatory_params(
    fct: Callable[..., object], expected: Tuple[str, ...]
) -> None:
    assert get_mandatory_params(fct) == expected
