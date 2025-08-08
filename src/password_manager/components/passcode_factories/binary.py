from collections.abc import Callable

from nicegui import ui

from . import Passcode


class BitString:
    """A string of bits."""

    def __init__(self) -> None:
        self._inner = 0
        self._shifts = 0

    def push(self, bit: bool) -> None:  # noqa: FBT001
        """Add a bit to this bitstring."""
        intbit = int(bit)
        self._inner |= intbit << self._shifts
        self._shifts += 1

    def to_passcode(self) -> Passcode:
        """Get the `Passcode` repr of this bitstring."""
        # passcodes are ints right now. we can do this trivially.
        return self._inner


def binaryinput_factory(submit_passcode: Callable[[Passcode], None]) -> ui.element:
    """Just a boring normal text box for testing purposes."""
    bits = BitString()

    def update_bits_then_submit(bit: bool) -> None:  # noqa: FBT001
        bits.push(bit)
        submit_passcode(bits.to_passcode())

    with ui.button_group() as factory:
        ui.button("0", on_click=lambda: update_bits_then_submit(bit=False))
        ui.button("1", on_click=lambda: update_bits_then_submit(bit=True))

    return factory
