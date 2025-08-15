from copy import deepcopy
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, NoReturn, TypeVar


def todo(msg: str = "") -> NoReturn:
    """Mark unimplemented code and let things type check.

    This is similar in usage and intent to Rust's `todo!()` macro, if one is familiar.
    Very useful during development.

    # Examples

    Stubbing:
    ```python
    def stub_thing() -> int:
        '''this type checks!'''
        todo()

    ```

    Inside functions:
    ```python
    "my-string".find(todo()) # this also type checks!

    ```
    """
    msg = f"TODO: {msg}"
    raise NotImplementedError(msg)


T = TypeVar("T")


def dbg(x: T) -> T:
    print(x)
    return x


@dataclass
class Ref(Generic[T]):
    """An owned reference to a value, or something."""

    inner: T
