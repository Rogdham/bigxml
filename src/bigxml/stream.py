from io import IOBase

from bigxml.utils import autostart_generator


@autostart_generator
def _flatten_stream(stream):
    yield

    # bytes-like
    try:
        yield memoryview(stream)
        return
    except TypeError:
        pass

    # file-like
    if hasattr(stream, "read"):
        while True:
            size = yield
            data = stream.read(size)
            if not data:
                break  # EOF
            try:
                yield memoryview(data)
            except TypeError as ex:
                if isinstance(data, str):
                    raise TypeError(
                        "Stream read method returned a str, not a bytes-like object."
                        " For files objects, open in binary mode."
                        " Else, you can try using codecs.getwriter."
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
        substreams = iter(stream)
    except TypeError:
        # other types not supported
        # pylint: disable=raise-missing-from
        raise TypeError(f"Invalid stream type: {type(stream).__name__}")

    for substream in substreams:
        yield from _flatten_stream(substream)


@autostart_generator
def _convert_to_read(data_stream):
    size = yield
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
    def __init__(self, *streams):
        super().__init__()
        self._read = _convert_to_read(_flatten_stream(streams))

    def read(self, size=None):
        if not isinstance(size, int) or size <= 0:
            raise NotImplementedError("Read size must be strictly positive")
        return self._read.send(size)

    @staticmethod
    def readable():
        return True
