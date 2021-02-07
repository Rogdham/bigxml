from inspect import signature
from typing import List

import pytest

from bigxml.utils import get_mandatory_params

# pylint: disable=unused-argument


def fct0():
    pass


def fct1(arg0):
    pass


def fct2(arg0, arg1, arg2):
    pass


def fct3(arg0=13, arg1=37, arg2=42):
    pass


def fct4(arg0, /, arg1, *, arg2, arg3=3):
    pass


def fct5(arg0, /, arg1, *arg2, arg3, arg4=4, **arg5):
    pass


def fct6(
    arg0: int,
    /,
    arg1: int,
    *arg2: List[int],
    arg3: int,
    arg4: int = 4,
    **arg5: List[int],
):
    pass


# pylint: enable=unused-argument


@pytest.mark.parametrize(
    "fct, expected",
    (
        (fct0, ()),
        (fct1, ("arg0",)),
        (fct2, ("arg0", "arg1", "arg2")),
        (fct3, ()),
        (fct4, ("arg0", "arg1", "arg2")),
        (fct5, ("arg0", "arg1", "arg3")),
        (fct6, ("arg0", "arg1", "arg3")),
    ),
    ids=lambda x: str(signature(x) if callable(x) else x),
)
def test_mandatory_params(fct, expected):
    assert get_mandatory_params(fct) == expected
