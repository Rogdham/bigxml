import pytest

from bigxml.utils import dictify


def test_base():
    assert dictify(
        (
            (("a", "b"), 0),
            (("a", "c", "d"), 1),
            (("a", "c", "e"), 2),
            (("a", "e"), 3),
            (("c",), 4),
            (("d", "f"), 5),
        )
    ) == {
        "a": {
            "b": 0,
            "c": {
                "d": 1,
                "e": 2,
            },
            "e": 3,
        },
        "c": 4,
        "d": {
            "f": 5,
        },
    }


def test_multiple_iterators():
    def gen_x():
        yield (("a", "b"), 0)
        yield (("c", "d"), 1)

    def gen_y():
        yield (("a", "e"), 2)

    def gen_z():
        yield (("c", "f"), 3)

    assert dictify(gen_x(), gen_y(), gen_z()) == {
        "a": {
            "b": 0,
            "e": 2,
        },
        "c": {
            "d": 1,
            "f": 3,
        },
    }


def test_collide_item():
    with pytest.raises(TypeError):
        dictify(
            (
                (("a", "b"), 0),
                # same path
                (("a", "b"), 1),
            )
        )


def test_collide_parent():
    with pytest.raises(TypeError):
        dictify(
            (
                (("a", "b", "c"), 0),
                # higher path
                (("a", "b"), 1),
            )
        )


def test_collide_child():
    with pytest.raises(TypeError):
        dictify(
            (
                (("a", "b"), 0),
                # lower path
                (("a", "b", "c"), 1),
            )
        )


def test_empty_path():
    with pytest.raises(TypeError):
        dictify(
            (
                # empty path
                ((), 0),
            )
        )


def test_dict_items():
    with pytest.raises(TypeError):
        dictify(
            (
                # dict item
                (("a", "b"), {"foo": "bar"}),
            )
        )
