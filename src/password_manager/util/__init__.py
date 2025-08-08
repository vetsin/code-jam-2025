from typing import NoReturn


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
