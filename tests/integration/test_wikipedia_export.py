from datetime import datetime
from lzma import LZMAFile
from pathlib import Path

from bigxml import XMLHandler, parse, xml_handle_element, xml_handle_text


def test_wikipedia_export():
    class Revision(XMLHandler):
        def __init__(self):
            self.author = None
            self.date = None

        @xml_handle_text("contributor", "username")
        def handle_author(self, node):
            self.author = node.text

        @xml_handle_text("timestamp")
        def handle_date(self, node):
            self.date = datetime.strptime(node.text, r"%Y-%m-%dT%H:%M:%SZ")

    class Handler(XMLHandler):
        # pylint: disable=no-self-use
        @xml_handle_element("mediawiki", "page", "revision")
        def handle_page(self, node):
            revision = Revision()
            yield from node.handle(revision)
            yield (revision.date, revision.author)

    with LZMAFile(Path(__file__).parent / "wikipedia_python_export.xml.xz") as f_in:
        items = list(parse(f_in, Handler()))
        assert len(items) == 1000
        last_item = items[-1]
        assert last_item[0].year == 2006
        assert last_item[0].month == 4
        assert last_item[0].day == 14
        assert last_item[0].hour == 15
        assert last_item[0].minute == 58
        assert last_item[1] == "Lulu of the Lotus-Eaters"
