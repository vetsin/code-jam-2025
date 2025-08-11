from collections.abc import Callable

from nicegui import ui

from password_manager.types import PasscodeInput, Passcode


def str_to_passcode(s: str) -> Passcode:
    """Convert a str to a passcode."""
    return s.encode("utf-8")


class TextInput(PasscodeInput):
    @staticmethod
    def get_name() -> str:
        return "Text"

    def __init__(self, on_submit: Callable[[bytes], None], submit_text: str) -> None:
        """Just a boring normal text box for testing purposes."""
        ui.input(
            label="enter password",
            on_change=lambda e: on_submit(str_to_passcode(e.value)),
        )
