from bigxml.utils import extract_namespace_name


def test_no_namespace() -> None:
    assert extract_namespace_name("foo") == ("", "foo")


def test_namespace() -> None:
    assert extract_namespace_name("{https://example.com/xml/}foo") == (
        "https://example.com/xml/",
        "foo",
    )


def test_empty_namespace() -> None:
    assert extract_namespace_name("{}foo") == ("", "foo")
