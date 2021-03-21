<div align="center" size="15px">

# BigXML

Parse big xml files and streams with ease

[![GitHub build status](https://img.shields.io/github/workflow/status/rogdham/bigxml/build/master)](https://github.com/rogdham/bigxml/actions?query=branch:master)&nbsp;[![Release on PyPI](https://img.shields.io/pypi/v/bigxml)](https://pypi.org/project/bigxml/)&nbsp;[![Code coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/rogdham/bigxml/search?q=fail+under&type=Code)&nbsp;[![MIT License](https://img.shields.io/pypi/l/bigxml)](https://github.com/Rogdham/bigxml/blob/master/LICENSE.txt)

---

[:book: Documentation](https://bigxml.rogdham.net/)&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;[:page_with_curl: Changelog](./CHANGELOG.md)

</div>

---

Parsing big XML files in Python is hard. On one hand, regular XML libraries load the
whole file into memory, which will crash the process if the file is too big. Other
solutions such as `iterparse` do read the file as they parse it, but they are complex to
use if you don't want to run out of memory.

This is where the _BigXML_ library shines:

- Works with XML files of any size
- No need to do memory management yourself
- Pythonic API
- Any stream can easily be parsed, not just files
- Secure from usual attacks against XML parsers
