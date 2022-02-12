from collections import deque
from functools import wraps
from inspect import Parameter, signature
import re


class IterWithRollback:
    def __init__(self, iterable):
        self.iteration = 0
        self._iterator = iter(iterable)
        self._can_rollback = False
        self._item_rollback = False
        self._last_item = None

    def __iter__(self):
        return self

    def rollback(self):
        if self._can_rollback:
            self.iteration -= 1
            self._can_rollback = False
            self._item_rollback = True

    def __next__(self):
        if not self._item_rollback:
            self._last_item = next(self._iterator)
        self.iteration += 1
        self._can_rollback = True
        self._item_rollback = False
        return self._last_item


_EXTRACT_NAMESPACE_REGEX = re.compile(r"^\{([^}]*)\}(.*)$")


def extract_namespace_name(name):
    match = _EXTRACT_NAMESPACE_REGEX.match(name)
    if match:
        return match.groups()
    return ("", name)


def last_item_or_none(iterable):
    try:
        return deque(iterable, maxlen=1)[0]
    except IndexError:
        return None


def consume(iterable):
    iterator = iter(iterable)
    try:
        next(iterator)
    except StopIteration:
        return False
    last_item_or_none(iterator)
    return True


def transform_to_iterator(fct):
    @wraps(fct)
    def wrapped(*args, **kwargs):
        return_value = fct(*args, **kwargs)
        if return_value is None:
            return iter(())  # empty iterator
        return iter(return_value)

    return wrapped


def get_mandatory_params(fct):
    try:
        sig = signature(fct)
    except (ValueError, TypeError):
        return ()  # e.g. for built-in
    return tuple(
        param.name
        for param in sig.parameters.values()
        if param.kind
        in (
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.KEYWORD_ONLY,
        )
        and param.default == sig.empty
    )


def autostart_generator(fct):
    @wraps(fct)
    def wrapped(*args, **kwargs):
        generator = fct(*args, **kwargs)
        if next(generator) is not None:
            raise ValueError("First item yielded by generator not None")
        return generator

    return wrapped
