from io import IOBase
from typing import Any, Generator, Iterable, Optional, cast

from bigxml.typing import Streamable, SupportsRead
from bigxml.utils import autostart_generator


@autostart_generator
def _flatten_stream(stream: Streamable) -> Generator[Optional[memoryview], int, None]:
    yield None

    # bytes-like
    try:
        yield memoryview(cast(bytes, stream))
        return  # noqa: TRY300
    except TypeError:
        pass

    # file-like
    if hasattr(stream, "read"):
        while True:
            size = yield None
            data = cast(SupportsRead[Any], stream).read(size)
            if not data:
                break  # EOF
            try:
                yield memoryview(data)
            except TypeError as ex:
                if isinstance(data, str):
                    raise TypeError(
                        "Stream read method returned a str, not a bytes-like object."
                        " Open file objects in binary mode."
                    ) from ex
                raise TypeError(
                    "Stream read method did not return a byte-like object:"
                    f" {type(data).__name__}"
                ) from ex
        return

    # known invalid type (need to be caught here since they are iterable)
    # we disallow sets to avoid issues with ordering
    if isinstance(stream, (str, set, dict)):
        if isinstance(stream, str):
            raise TypeError(
                "Invalid stream type: str."
                " Convert it to a bytes-like object by encoding it."
            )
        raise TypeError(f"Invalid stream type: {type(stream).__name__}")

    # stream iterator (recursive)
    try:
        substreams = iter(cast(Iterable[Streamable], stream))
    except TypeError:
        # other types not supported
        raise TypeError(f"Invalid stream type: {type(stream).__name__}") from None

    for substream in substreams:
        yield from _flatten_stream(substream)


@autostart_generator
def _convert_to_read(
    data_stream: Generator[Optional[memoryview], int, None]
) -> Generator[bytes, int, None]:
    size = yield b""
    while True:
        try:
            buffer = data_stream.send(size)
        except StopIteration:
            break

        while buffer:
            data, buffer = buffer[:size], buffer[size:]
            size = yield data.tobytes()

    while True:
        yield b""


class StreamChain(IOBase):
    def __init__(self, *streams: Streamable) -> None:
        super().__init__()
        self._read = _convert_to_read(_flatten_stream(streams))

    def read(self, size: Optional[int] = None) -> bytes:
        if not isinstance(size, int) or size <= 0:
            raise NotImplementedError("Read size must be strictly positive")
        return self._read.send(size)

    @staticmethod
    def readable() -> bool:
        return True
