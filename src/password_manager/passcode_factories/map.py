from collections.abc import Callable

from . import Passcode


def map_lock_factory(submit_passcode: Callable[[Passcode], None]) -> None:
    """See https://github.com/vetsin/code-jam-2025/issues/6."""
