from dataclasses import is_dataclass
from inspect import getmembers, isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)
import warnings

from bigxml.marks import get_marks, has_marks
from bigxml.typing import T
from bigxml.utils import consume, get_mandatory_params, transform_to_iterator

if TYPE_CHECKING:
    from bigxml.nodes import XMLElement, XMLText

CLASS_HANDLER_METHOD_NAME = "xml_handler"


def _assert_one_mandatory_param(
    mandatory_params: Tuple[str, ...], klass: Type[Any], method_name: str
) -> None:
    if len(mandatory_params) > 1:
        raise TypeError(
            f"Invalid class method: {klass.__name__}.{method_name}"
            " should have no or one mandatory parameters, got:"
            f" {', '.join(mandatory_params)}"
        )


def _assert_iterable_or_none(
    item: object, klass: Type[Any], method_name: str
) -> Optional[Iterable[object]]:
    if item is None or isinstance(item, Iterable):
        return item
    raise TypeError(
        f"Invalid_class method: {klass.__name__}.{method_name}"
        " should have returned None or an iterable"
    )


def _handler_identity(node: T) -> Iterator[T]:
    yield node


class _HandlerTree:
    def __init__(self, path: Tuple[str, ...] = ()) -> None:
        self.path: Tuple[str, ...] = path
        self.children: Dict[str, _HandlerTree] = {}
        self.handler: Optional[Callable[..., Iterable[object]]] = None

    def add_handler(
        self,
        path: Tuple[str, ...],
        handler: object,
        *,
        ignore_direct_marks: bool,
    ) -> None:
        # marked
        marks = () if ignore_direct_marks else get_marks(handler)
        if marks:
            for mark in marks:
                self.add_handler(path + mark, handler, ignore_direct_marks=True)
            return

        # callable
        if callable(handler):
            self.add_handler_callable(path, handler)
            return

        # object with marks
        found = False
        for handler_name, sub_handler in getmembers(handler):
            if handler_name.startswith("__"):
                continue
            for sub_path in get_marks(sub_handler):
                self.add_handler(path + sub_path, sub_handler, ignore_direct_marks=True)
                found = True
        if found:
            return

        # syntactic sugar
        if isinstance(handler, str):
            handler = (handler,)
        if isinstance(handler, list):
            handler = tuple(handler)
        if isinstance(handler, tuple):
            self.add_handler(
                path + handler,
                _handler_identity,
                ignore_direct_marks=True,  # does not matter as _handler_identity has no marks
            )
            return

        # other types
        raise TypeError(f"Invalid handler type: {type(handler).__name__}")

    def add_handler_callable(
        self,
        path: Tuple[str, ...],
        handler: Callable[..., Iterable[object]],
    ) -> None:
        if self.handler:
            raise TypeError(f"{self.path}: catchall handler exists: {self.handler}")
        if path:
            if path[0] not in self.children:
                self.children[path[0]] = _HandlerTree((*self.path, path[0]))
            self.children[path[0]].add_handler(
                path[1:], handler, ignore_direct_marks=True
            )
        elif self.children:
            raise TypeError(f"{self.path}: handlers exist: {self.children}")
        else:
            self.handler = handler

    @transform_to_iterator
    def handle(
        self, node: Union["XMLElement", "XMLText"]
    ) -> Optional[Iterable[object]]:
        if self.handler:
            if isclass(self.handler):
                return self._handle_from_class(self.handler, node)
            return self.handler(node)

        child: Optional[_HandlerTree] = None
        namespace = getattr(node, "namespace", None)
        if namespace is not None:
            child = self.children.get(f"{{{namespace}}}{node.name}")
        if child is None:
            child = self.children.get(node.name)
        if child is not None:
            if child.handler:
                return child.handle(node)
            if hasattr(node, "iter_from"):
                # it would have been better to test for isinstance(node, XMLElement)
                # to avoid the cast but that would have been a cyclic import
                return cast("XMLElement", node).iter_from(child.handle)
        return None

    @staticmethod
    def _handle_from_class(  # type: ignore[misc]
        klass: Type[Any], node: Union["XMLElement", "XMLText"]
    ) -> Optional[Iterable[object]]:
        # instantiate class
        init_mandatory_params = get_mandatory_params(klass)
        try:
            _assert_one_mandatory_param(init_mandatory_params, klass, "__init__")
        except TypeError as ex:
            if is_dataclass(klass):
                raise TypeError(
                    f"{ex}. Add a default value for dataclass fields."
                ) from ex
            raise
        instance = klass(node) if init_mandatory_params else klass()

        # create handler tree
        sub_tree = _HandlerTree()
        items: Iterable[object] = ()  # empty iterable
        try:
            sub_tree.add_handler((), instance, ignore_direct_marks=True)
        except TypeError:
            pass  # no marks on public attributes
        else:
            if has_marks(klass):
                if hasattr(node, "iter_from"):
                    # it would have been better to test for isinstance(node, XMLElement)
                    items = cast("XMLElement", node).iter_from(sub_tree.handle)
            else:
                items = sub_tree.handle(node)

        # handle custom handler method
        wrapper = getattr(instance, CLASS_HANDLER_METHOD_NAME, None)
        if wrapper is not None:
            wrapper_mandatory_params = get_mandatory_params(wrapper)
            _assert_one_mandatory_param(
                wrapper_mandatory_params,
                klass,
                CLASS_HANDLER_METHOD_NAME,
            )
            if wrapper_mandatory_params:
                return _assert_iterable_or_none(
                    wrapper(items), klass, CLASS_HANDLER_METHOD_NAME
                )

        # no custom wrapper or custom wrapper does not handle items
        # warn if some items have been yielded by sub-handlers
        # because they are being completely ignored
        if consume(items):
            warning_msg = (
                "Items were yielded by some sub-handler"
                f" of class {instance.__class__.__name__}."
            )
            if wrapper is None:
                warning_msg += (
                    f" Add an argument to the {CLASS_HANDLER_METHOD_NAME}"
                    " method to handle them properly."
                )
            else:
                warning_msg += (
                    f" Create a {CLASS_HANDLER_METHOD_NAME}"
                    " method to handle them properly."
                )
            warnings.warn(warning_msg, UserWarning, stacklevel=1)

        if wrapper is None:
            # no custom wrapper: only yield instance
            return (instance,)
        return _assert_iterable_or_none(wrapper(), klass, CLASS_HANDLER_METHOD_NAME)


def create_handler(
    *args: object,
) -> Callable[[Union["XMLElement", "XMLText"]], Iterator[object]]:
    handler_tree = _HandlerTree()
    for arg in args:
        handler_tree.add_handler((), arg, ignore_direct_marks=False)
    return handler_tree.handle
