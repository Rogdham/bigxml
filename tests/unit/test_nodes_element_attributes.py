import pytest

from bigxml.nodes import XMLElementAttributes

ATTRIBUTES = {
    # no namespace
    r"aaa": "0",
    # one namespace
    r"{xxx}bbb": "1",
    # several namespaces
    r"{xxx}ccc": "2",
    r"{yyy}ccc": "3",
    # different path in code depending on order of key without namespace
    # prefer no namespace (1)
    r"ddd": "4",
    r"{xxx}ddd": "5",
    r"{yyy}ddd": "6",
    # prefer no namespace (2)
    r"{xxx}eee": "7",
    r"eee": "8",
    r"{yyy}eee": "9",
    # prefer no namespace (3)
    r"{xxx}fff": "10",
    r"{yyy}fff": "11",
    r"fff": "12",
}
XML_ELEMENT_ATTRIBUTES = XMLElementAttributes(ATTRIBUTES)


@pytest.mark.parametrize(
    "key, value, should_warn",
    (
        ("aaa", "0", False),
        ("bbb", "1", False),
        ("ccc", "2", True),
        ("ddd", "4", False),
        ("eee", "8", False),
        ("fff", "12", False),
    ),
    ids=(
        "no namespace",
        "one namespace",
        "several namespaces",
        "prefer no namespace (1)",
        "prefer no namespace (2)",
        "prefer no namespace (3)",
    ),
)
def test_get_without_namespace(key, value, should_warn):
    if should_warn:
        with pytest.warns(RuntimeWarning):
            assert XML_ELEMENT_ATTRIBUTES[key] == value
    else:
        assert XML_ELEMENT_ATTRIBUTES[key] == value


@pytest.mark.parametrize(
    "key, value",
    ((k if k[0] == "{" else "{{}}{}".format(k), v) for k, v in ATTRIBUTES.items()),
)
def test_get_with_namespace(key, value):
    assert XML_ELEMENT_ATTRIBUTES[key] == value


def test_iter():
    assert set(iter(XML_ELEMENT_ATTRIBUTES)) == set(ATTRIBUTES.keys())


def test_len():
    assert len(XML_ELEMENT_ATTRIBUTES) == 13


def test_eq():
    i = XMLElementAttributes({"foo": "bar"})
    assert i == i  # pylint: disable=comparison-with-itself
    assert i == XMLElementAttributes(i)

    j = XMLElementAttributes({r"{}foo": "bar"})
    assert j == j  # pylint: disable=comparison-with-itself
    assert j == XMLElementAttributes(j)

    assert i == j
    assert XMLElementAttributes(i) == j
    assert i == XMLElementAttributes(j)
    assert XMLElementAttributes(i) == XMLElementAttributes(j)
