import pytest

from bigxml.nodes import XMLElementAttributes

ATTRIBUTES = {
    # no namespace
    "aaa": "0",
    # one namespace
    "{xxx}bbb": "1",
    # several namespaces
    "{xxx}ccc": "2",
    "{yyy}ccc": "3",
    # different path in code depending on order of key without namespace
    # prefer no namespace (1)
    "ddd": "4",
    "{xxx}ddd": "5",
    "{yyy}ddd": "6",
    # prefer no namespace (2)
    "{xxx}eee": "7",
    "eee": "8",
    "{yyy}eee": "9",
    # prefer no namespace (3)
    "{xxx}fff": "10",
    "{yyy}fff": "11",
    "fff": "12",
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
    ((k if k[0] == "{" else f"{{}}{k}", v) for k, v in ATTRIBUTES.items()),
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

    j = XMLElementAttributes({"{}foo": "bar"})
    assert j == j  # pylint: disable=comparison-with-itself
    assert j == XMLElementAttributes(j)

    assert i == j
    assert XMLElementAttributes(i) == j
    assert i == XMLElementAttributes(j)
    assert XMLElementAttributes(i) == XMLElementAttributes(j)
