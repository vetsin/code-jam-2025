from collections.abc import Callable

from nicegui import ui

from . import Passcode


def str_to_passcode(s: str) -> Passcode:
    """Convert a str to a passcode."""
    return int.from_bytes(bytearray(s, "utf-8"), byteorder="big", signed=False)


def textinput_factory(submit_passcode: Callable[[Passcode], None]) -> ui.element:
    """Just a boring normal text box for testing purposes."""
    return ui.input(
        label="enter password",
        # placeholder="start typing",  # noqa: ERA001
        on_change=lambda e: submit_passcode(str_to_passcode(e.value)),
    )
