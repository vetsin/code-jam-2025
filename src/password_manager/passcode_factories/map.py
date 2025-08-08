from collections.abc import Callable


def map_lock_factory(success: Callable[[], None], failure: Callable[[], None]) -> None:
    """See https://github.com/vetsin/code-jam-2025/issues/6."""
