# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [0.10.0] - 2023-04-22

[0.10.0]: https://github.com/rogdham/bigxml/compare/v0.9.0...v0.10.0

### :boom: Breaking changes

- Renamed the base class for exceptions to `BigXmlError` in conformance with PEP8

### :rocket: Added

- Add documentation to explain how to import the library
- Warnings due to wrong usage are now using `UserWarning` instead of `RuntimeWarning`
- Undocumented parameter `insecurely_allow_entities` to `Parser`

### :house: Internal

- Necessary code changes following dev dependency update: mypy
- Use ruff for linting (and remove isort)

## [0.9.0] - 2022-11-06

[0.9.0]: https://github.com/rogdham/bigxml/compare/v0.8.0...v0.9.0

v0.9.0 introduces custom exceptions.

### :boom: Breaking changes

- All exceptions raised due to invalid stream content are now instances of
  `BigXmlException` instead of `xml.etree.ElementTree.ParseError` or
  `defusedxml.DefusedXmlException`.

### :bug: Fixes

- Add a workaround against pylint `not-an-iterable` false-positive on `iter_from`

### :house: Internal

- Necessary code changes following dev dependency update: mypy, pylint, pytest
- Add tests for CPython 3.11
- Use CPython 3.11 for misc. tests
- Update Github actions dependencies

## [0.8.0] - 2022-08-28

[0.8.0]: https://github.com/rogdham/bigxml/compare/v0.7.0...v0.8.0

v0.8.0 brings type hints!

### :boom: Breaking changes

- End of Python 3.6 support

### :bug: Fixes

- Fix an edge case when a class decorated with `xml_handle_text` has an attribute
  decorated with `xml_handle_element`

### :rocket: Added

- Type hints
- New export: `HandlerTypeHelper` that can help with type hints in some cases
- Sanity check on `xml_handler` method of class handlers for returned values (`None` or
  an iterable)

### :house: Internal

- Add tests for PyPy 3.9
- Refactor handler creator code
- Type validation with mypy
- Distribute `py.typed` file in conformance with [PEP 561]
- Update `typing-extensions` dependency

[pep 561]: https://www.python.org/dev/peps/pep-0561/

## [0.7.0] - 2022-01-15

[0.7.0]: https://github.com/rogdham/bigxml/compare/v0.6.1...v0.7.0

v0.7.0 improves dependencies requirements.

### :rocket: Added

- Don't use upper bound constraints on dependencies
- Specify the Python versions required in package metadata

### :house: Internal

- Improving memory consumption tests by using `tracemalloc` instead of `resource`

## [0.6.1] - 2022-01-01

[0.6.1]: https://github.com/rogdham/bigxml/compare/v0.6.0...v0.6.1

v0.6.1 is a minor release.

### :house: Internal

- Don't deploy src dir for docs
- Fix minor issues found by automated tools
- Add tests for CPython 3.10 and PyPy 3.8
- Use CPython 3.10 for misc. tests
- Clarify which Python versions are supported in docs
- Update `dataclasses` dependency (Python 3.6 only)

## [0.6.0] - 2021-03-21

[0.6.0]: https://github.com/rogdham/bigxml/compare/v0.5.0...v0.6.0

v0.6.0 adds documentation!

### :boom: Breaking changes

- Classes as handlers without a `xml_handler` method now yield the instance instead of
  items yielded by sub-handlers

### :bug: Fixes

- An exception was raised when using a class handlers without any sub-handler attributes
- Fix an error in some Python version for class handlers extending some builtins without
  redefining `__init__`

### :memo: Documentation

- Add detailed documentation, available online at <https://bigxml.rogdham.net/>

### :house: Internal

- Test against some XML attacks
- Tests are now run in Python Development Mode
- Update `defusedxml` dependency

## [0.5.0] - 2021-03-01

[0.5.0]: https://github.com/rogdham/bigxml/compare/v0.4.0...v0.5.0

v0.5.0 allows more stream types to be parsed.

### :boom: Breaking changes

- `Parser` can not longer be instantiated with a file-like object opened in text mode,
  nor with a filename
- Removed `stream` attribute from `Parser` instances

### :rocket: Added

- `Parser` can now be instantiated with several streams as arguments: in that case the
  streams are concatenated: after the end of a stream, data is taken from the next one
- More variety in stream types passed as argument of `Parser`:
  - File-like objects opened in binary mode (was already supported before)
  - Bytes-like objects (e.g. `bytes` or `bytearray` instances)
  - Iterable of previous types (recursively)

## [0.4.0] - 2021-02-14

[0.4.0]: https://github.com/rogdham/bigxml/compare/v0.3.0...v0.4.0

v0.4.0 is a major refactor in handler types.

### :boom: Breaking changes

- `XMLHandler` has been removed: class handlers don't need to inherit from it anymore
- `return_from` now returns the last yielded item instead of the handler
- `HandleMgr` no longer has the confusing `set_handle` method

### :rocket: Added

- Several handlers can now be passed to `return_from` / `iter_from`
- More handler variety:
  - Regular functions
  - `str`/`tuple`/`list` are syntactic sugar for a handler marked with that value, which
    simply yields the node
  - Classes are instantiated on the fly (if `__init__` has one mandatory parameter, the
    node is passed during instantiation); in that case, a `xml_handler` method can be
    defined to customize the way yielded items are handled
- It is now possible to use directly `@xml_handle_text` in place of `@xml_handle_text()`
- Python 3.9 support

## [0.3.0] - 2020-09-27

[0.3.0]: https://github.com/rogdham/bigxml/compare/v0.2.0...v0.3.0

v0.3.0 improves namespace support.

### :boom: Breaking changes

- `XMLElement`'s `namespace` attribute is now an empty string instead of `None` when the
  node has no namespace

### :rocket: Added

- Better namespace support in `XMLElement`'s attributes
- Namespace support in `xml_handle_*`
- More readable `__str__` values for `XMLElement` and `XMLText`

### :bug: Fixes

- Fix `xml_handle_*` when wrapping `staticmethod` (other way around was already working
  properly)

## [0.2.0] - 2020-09-06

[0.2.0]: https://github.com/rogdham/bigxml/compare/v0.1.0...v0.2.0

v0.2.0 changes the API to makes `iter_from` and `return_from` methods available on both
`Parser` and `XMLElement` instances.

### :boom: Breaking changes

- `XMLElement`'s `handle` method is renamed to `iter_from`
- The `parse` function has been removed in favour of the new `Parser` class; use
  `Parser(stream).iter_from(handler)` instead of `parse(stream, handler)`

### :rocket: Added

- `XMLElement` now has a `text` property to walk through all children and gather texts
  regardless of the tags
- `XMLElement` new `return_from` method can be used when there are no items yielded by
  the handler
- PyPy support

### :bug: Fixes

- An exception is now raised when a node is accessed out of order; this avoids
  inconsistent behaviors in some cases, and replaces the obscure `No handle to use`
  exception in other cases

### :memo: Documentation

- Add changelog file

## [0.1.0] - 2020-08-23

[0.1.0]: https://github.com/rogdham/bigxml/releases/tag/v0.1.0

### :rocket: Added

- Initial public release :tada:
