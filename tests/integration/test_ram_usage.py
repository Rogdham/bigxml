from typing import Callable, Iterator

import pytest

from bigxml import Parser, XMLText, xml_handle_text


@pytest.fixture
def ram_usage() -> Iterator[Callable[[], float]]:
    try:
        import tracemalloc  # pylint: disable=import-outside-toplevel
    except ImportError:  # e.g. PyPy
        pytest.skip("tracemalloc module not available")

    try:
        tracemalloc.start()
        yield lambda: tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()


def big_stream(ram_used: Callable[[], float]) -> Iterator[bytes]:
    ram_limit: float | None = None

    yield b"<root>\n"

    for i in range(100):  # 10Mb * 100 -> 1Gb read
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

        if ram_limit is None:
            ram_limit = ram_used() * 2  # should be enough
        else:
            assert ram_used() < ram_limit, "Consumes too much RAM"

    yield b"</root>"


def test_with_handler(
    # pylint: disable=redefined-outer-name
    ram_usage: Callable[[], float],
) -> None:
    @xml_handle_text("root", "entry", "nb")
    def handler(node: XMLText) -> Iterator[int]:
        yield int(node.text)

    items = Parser(big_stream(ram_usage)).iter_from(handler)

    for exp, item in enumerate(items):
        assert item == exp


def test_no_handler(
    # pylint: disable=redefined-outer-name
    ram_usage: Callable[[], float],
) -> None:
    items: Iterator[object] = Parser(big_stream(ram_usage)).iter_from()
    assert not list(items)
