import resource

from bigxml import Parser, xml_handle_text


def ram_used():
    # https://stackoverflow.com/a/7669482
    # we don't care about the exact value nor the unit
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def big_stream():
    ram_limit = ram_used() * 4  # should be enough

    yield b"<root>\n"

    for i in range(100):  # 10Mb * 100 -> 1Gb read
        assert ram_used() < ram_limit, "Consumes too much RAM"

        entry = b"".join(
            (
                b"<entry>\n",
                b"\n".join(
                    b"<a%d>%s</a%d>" % (j, (b"a%d" % j) * 100_000, j) for j in range(37)
                ),
                b"\n<nb>%d</nb>\n" % i,
                b"</entry>\n",
            )
        )
        assert 10_000_000 < len(entry) < 11_000_000  # each entry is about 10Mb

        yield entry

    yield b"</root>"


def test_with_handler():
    @xml_handle_text("root", "entry", "nb")
    def handler(node):
        yield int(node.text)

    items = Parser(big_stream()).iter_from(handler)

    for exp, item in enumerate(items):
        assert item == exp


def test_no_handler():
    items = Parser(big_stream()).iter_from()
    assert list(items) == []
