# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

[unreleased]: https://github.com/rogdham/bigxml/compare/v0.4.0...HEAD

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
  - `str`/`tuple`/`list` are syntactic sugar for a handler marked with that value,
    which simply yields the node
  - Classes are instantiated on the fly (if `__init__` has one mandatory parameter,
    the node is passed during instantiation); in that case, a `xml_handler` method can
    be defined to customize the way yielded items are handled
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

- Fix `xml_handle_*` when wrapping `staticmethod` (other way around was already
  working properly)

## [0.2.0] - 2020-09-06

[0.2.0]: https://github.com/rogdham/bigxml/compare/v0.1.0...v0.2.0

v0.2.0 changes the API to makes `iter_from` and `return_from` methods
available on both `Parser` and `XMLElement` instances.

### :boom: Breaking changes

- `XMLElement`'s `handle` method is renamed to `iter_from`
- The `parse` function has been removed in favour of the new `Parser` class;
  use `Parser(stream).iter_from(handler)` instead of `parse(stream, handler)`

### :rocket: Added

- `XMLElement` now has a `text` property
  to walk through all children and gather texts regardless of the tags
- `XMLElement` new `return_from` method
  can be used when there are no items yielded by the handler
- PyPy support

### :bug: Fixes

- An exception is now raised when a node is accessed out of order;
  this avoids inconsistent behaviors in some cases,
  and replaces the obscure `No handle to use` exception in other cases

### :memo: Documentation

- Add changelog file

## [0.1.0] - 2020-08-23

[0.1.0]: https://github.com/rogdham/bigxml/releases/tag/v0.1.0

### :rocket: Added

- Initial public release :tada:
