from collections.abc import Callable

from password_manager.types import PasscodeInput, Passcode


class DialSafe(PasscodeInput):
    @staticmethod
    def get_name() -> str:
        return "Dial Safe"

    def __init__(self, on_submit: Callable[[bytes], None], submit_text: str) -> None:
        """See https://github.com/vetsin/code-jam-2025/issues/7."""
