from collections import deque
from functools import wraps
from inspect import Parameter, signature
from itertools import chain
import re


def dictify(*items):
    final_dict = {}
    for parts, item in chain(*items):
        if not parts:
            raise TypeError("Empty part")
        if isinstance(item, dict):
            raise TypeError("Items cannot be dict instances")

        current_dict = final_dict
        current_path = []

        # go to deeper dict
        for part in parts[:-1]:
            current_path.append(part)
            if part in current_dict:
                if not isinstance(current_dict[part], dict):
                    raise TypeError(
                        f"{current_path} is set to item: {current_dict[part]}"
                    )
            else:
                current_dict[part] = {}
            current_dict = current_dict[part]

        # add item
        part = parts[-1]
        current_path.append(part)
        if part in current_dict:
            raise TypeError(f"{current_path} already exists: {current_dict[part]}")
        current_dict[part] = item

    return final_dict


class IterWithRollback:
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.iteration = 0
        self.first_iteration = True
        self.item_rollback = False
        self.current_item = None

    def __iter__(self):
        return self

    def rollback(self):
        if not self.first_iteration:
            self.iteration -= 1
            self.item_rollback = True

    def __next__(self):
        if self.item_rollback:
            self.item_rollback = False
            self.iteration += 1
            return self.current_item
        self.current_item = next(self.iterator)
        self.first_iteration = False
        self.iteration += 1
        return self.current_item


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


def transform_none_return_value(fct):
    @wraps(fct)
    def wrapped(*args, **kwargs):
        return_value = fct(*args, **kwargs)
        if return_value is None:
            return ()  # empty iterable
        return return_value

    return wrapped


def get_mandatory_params(fct):
    sig = signature(fct)
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
