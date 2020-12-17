from io import IOBase
import resource

import pytest

from bigxml import Parser, xml_handle_text


@pytest.fixture
def big_stream():
    class BigStream(IOBase):
        def __init__(self, nb_items):
            super().__init__()
            self.buf = b"<root>\n"
            self.pos = 0
            self.i = 0
            self.nb_items = nb_items
            self.ram_limit = self.ram_used() * 4  # should be enough

        @staticmethod
        def ram_used():
            # https://stackoverflow.com/a/7669482
            # we don't care about the exact value nor the unit
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        def generate_block(self):
            assert self.ram_used() < self.ram_limit, "Consumes too much RAM"
            self.i += 1
            if self.i > self.nb_items:
                return b"</root>"
            return b"".join(
                (
                    b"<entry>\n",
                    b"\n".join(
                        b"<a%d>%s</a%d>" % (j, (b"a%d" % j) * 100_000, j)
                        for j in range(37)
                    ),
                    b"\n<nb>%d</nb>\n" % (self.i - 1),
                    b"</entry>\n",
                )
            )

        @staticmethod
        def readable():
            return True

        def read(self, bytes_count):
            while self.pos + bytes_count > len(self.buf) and self.i <= self.nb_items:
                self.buf = self.buf[self.pos :] + self.generate_block()
                self.pos = 0
            self.pos += bytes_count
            return self.buf[self.pos - bytes_count : self.pos]

    # each entry is about 10Mb
    assert 10_000_000 < len(BigStream(1).generate_block()) < 11_000_000

    return BigStream(100)  # 10Mb * 100 -> 1Gb read


# pragma pylint: disable=redefined-outer-name


def test_ram_usage(big_stream):
    @xml_handle_text("root", "entry", "nb")
    def handler(node):
        yield int(node.text)

    items = Parser(big_stream).iter_from(handler)

    for exp, item in enumerate(items):
        assert item == exp


def test_ram_usage_no_handler(big_stream):
    items = Parser(big_stream).iter_from()
    assert list(items) == []
