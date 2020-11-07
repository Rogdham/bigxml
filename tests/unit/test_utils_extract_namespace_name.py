from bigxml.utils import extract_namespace_name


def test_no_namespace():
    assert extract_namespace_name("foo") == ("", "foo")


def test_namespace():
    assert extract_namespace_name("{http://example.com/xml/}foo") == (
        "http://example.com/xml/",
        "foo",
    )


def test_empty_namespace():
    assert extract_namespace_name("{}foo") == ("", "foo")
