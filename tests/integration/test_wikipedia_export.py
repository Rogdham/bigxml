from datetime import datetime
from lzma import LZMAFile
from pathlib import Path

from bigxml import Parser, XMLText, xml_handle_element, xml_handle_text


def test_wikipedia_export() -> None:
    @xml_handle_element("mediawiki", "page", "revision")
    class Revision:
        def __init__(self) -> None:
            self.author: str | None = None
            self.date: datetime | None = None

        @xml_handle_text("contributor", "username")
        def handle_author(self, node: XMLText) -> None:
            self.author = node.text

        @xml_handle_text("timestamp")
        def handle_date(self, node: XMLText) -> None:
            self.date = datetime.strptime(node.text, "%Y-%m-%dT%H:%M:%SZ").astimezone()

    with LZMAFile(Path(__file__).parent / "wikipedia_python_export.xml.xz") as stream:
        items = list(Parser(stream).iter_from(Revision))
        assert len(items) == 1000
        assert all(isinstance(item, Revision) for item in items)
        revision = items[-1]
        assert revision.author == "Lulu of the Lotus-Eaters"
        assert revision.date is not None
        assert revision.date.year == 2006
        assert revision.date.month == 4
        assert revision.date.day == 14
        assert revision.date.hour == 15
        assert revision.date.minute == 58
