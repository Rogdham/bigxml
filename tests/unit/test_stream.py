from io import BytesIO, IOBase, StringIO
from string import ascii_lowercase

import pytest

from bigxml.stream import StreamChain


def test_no_stream():
    stream = StreamChain()
    assert stream.readable() is True
    assert stream.read(42) == b""


def abcdef_generator():
    yield b"abcdef"


@pytest.mark.parametrize(
    "stream",
    (
        b"abcdef",
        bytearray(b"abcdef"),
        memoryview(b"abcdef"),
        BytesIO(b"abcdef"),
        [b"abcdef"],
        (b"abcdef",),
        iter([b"abcdef"]),
        abcdef_generator(),
    ),
    ids=type,
)
def test_types(stream):
    stream = StreamChain(stream)
    assert stream.read(42) == b"abcdef"
    assert stream.read(42) == b""


def abcdef_str_generator():
    yield "abcdef"


class IntIO(IOBase):
    @staticmethod
    def read(size):
        assert isinstance(size, int)
        assert size >= 0
        return 42

    @staticmethod
    def readable():
        return True

    @staticmethod
    def __repr__():
        return "IntIO()"


@pytest.mark.parametrize(
    "stream, err_message",
    (
        pytest.param("abcdef", "Convert it to a bytes-like object", id="str"),
        pytest.param(
            StringIO("abcdef"), "For files objects, open in binary mode", id="StringIO"
        ),
        pytest.param(["abcdef"], "Convert it to a bytes-like object", id="list[str]"),
        pytest.param(("abcdef",), "Convert it to a bytes-like object", id="tuple[str]"),
        pytest.param(
            iter(["abcdef"]), "Convert it to a bytes-like object", id="iter[str]"
        ),
        pytest.param(
            abcdef_str_generator(),
            "Convert it to a bytes-like object",
            id="generator[str]",
        ),
        pytest.param(None, "Invalid stream type: NoneType", id="None"),
        pytest.param(True, "Invalid stream type: bool", id="True"),
        pytest.param(False, "Invalid stream type: bool", id="False"),
        pytest.param(42, "Invalid stream type: int", id="int"),
        pytest.param({b"abcdef"}, "Invalid stream type: set", id="set"),
        pytest.param({b"abc": b"def"}, "Invalid stream type: dict", id="dict"),
        pytest.param(
            IntIO(), "Stream read method did not return a byte-like object", id="IntIo"
        ),
    ),
)
def test_types_invalid(stream, err_message):
    stream = StreamChain(stream)
    with pytest.raises(TypeError) as excinfo:
        stream.read(42)

    assert err_message in str(excinfo.value)


def op_qr_generator():
    yield b"op"
    yield b"qr"


def test_chain_types():
    stream = StreamChain(
        b"ab",
        bytearray(b"cd"),
        memoryview(b"ef"),
        BytesIO(b"gh"),
        [b"ij"],
        (b"kl",),
        iter([b"mn"]),
        op_qr_generator(),
    )
    assert stream.read(42) == b"ab"
    assert stream.read(42) == b"cd"
    assert stream.read(42) == b"ef"
    assert stream.read(42) == b"gh"
    assert stream.read(42) == b"ij"
    assert stream.read(42) == b"kl"
    assert stream.read(42) == b"mn"
    assert stream.read(42) == b"op"
    assert stream.read(42) == b"qr"
    assert stream.read(42) == b""


def test_skip_empty_values():
    stream = StreamChain(b"", b"", b"abc", b"", b"", b"def", b"", b"ghi", b"")
    assert stream.read(42) == b"abc"
    assert stream.read(42) == b"def"
    assert stream.read(42) == b"ghi"
    assert stream.read(42) == b""


def test_stream_part_above_read_size():
    stream = StreamChain(ascii_lowercase.encode())
    assert stream.read(4) == b"abcd"
    assert stream.read(8) == b"efghijkl"
    assert stream.read(2) == b"mn"
    assert stream.read(8) == b"opqrstuv"
    assert stream.read(1) == b"w"
    assert stream.read(8) == b"xyz"
    assert stream.read(8) == b""


class InfiniteIO(IOBase):
    @staticmethod
    def read(size):
        assert isinstance(size, int)
        assert 0 <= size < 16
        return (b"%x" % size) * size

    @staticmethod
    def readable():
        return True

    @staticmethod
    def __repr__():
        return "InfiniteIO()"


@pytest.mark.parametrize(
    "streams",
    (
        (BytesIO(b"***"), InfiniteIO()),
        (BytesIO(b"***"), [InfiniteIO()]),
        ([BytesIO(b"***"), InfiniteIO()]),
        (BytesIO(b"***"), [[InfiniteIO()]]),
        ([BytesIO(b"***"), [InfiniteIO()]]),
        ([[BytesIO(b"***"), InfiniteIO()]]),
        # same with b"" inserts
        (b"", b"", BytesIO(b"***"), b"", b"", InfiniteIO()),
        (b"", b"", BytesIO(b"***"), b"", b"", [InfiniteIO()]),
        (b"", b"", BytesIO(b"***"), b"", b"", [b"", b"", InfiniteIO()]),
        (b"", b"", [b"", b"", BytesIO(b"***"), b"", b"", InfiniteIO()]),
        (b"", b"", BytesIO(b"***"), b"", b"", [b"", b"", [InfiniteIO()]]),
        (b"", b"", [BytesIO(b"***"), b"", b"", [InfiniteIO()]]),
        (b"", b"", [b"", b"", BytesIO(b"***"), b"", b"", [InfiniteIO()]]),
        (b"", b"", [b"", b"", [BytesIO(b"***"), b"", b"", InfiniteIO()]]),
        (b"", b"", [b"", b"", [b"", b"", BytesIO(b"***"), b"", b"", InfiniteIO()]]),
    ),
    ids=repr,
)
def test_pass_read_size(streams):
    stream = StreamChain(*streams)
    assert stream.read(3) == b"***"
    assert stream.read(4) == b"4444"
    assert stream.read(8) == b"88888888"
    assert stream.read(2) == b"22"


@pytest.mark.parametrize("size", (None, -1, 0))
def test_invalid_read_sizes(size):
    stream = StreamChain(b"Hello, world!")
    with pytest.raises(NotImplementedError):
        stream.read(size)
