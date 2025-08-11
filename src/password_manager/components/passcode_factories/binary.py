from collections.abc import Callable

from nicegui import ui

from password_manager.types import PasscodeInput, Passcode

MAX_PASSCODE_BYTE_LIMIT = 20


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
        return self._inner.to_bytes(byteorder="big", length=MAX_PASSCODE_BYTE_LIMIT)


class BinaryInput(PasscodeInput):
    @staticmethod
    def get_name() -> str:
        return "Binary"

    def __init__(self, on_submit: Callable[[bytes], None], _submit_text: str) -> None:
        """Binary 0 and 1."""
        bits = BitString()

        def update_bits_then_submit(bit: bool) -> None:  # noqa: FBT001
            bits.push(bit)
            on_submit(bits.to_passcode())

        with ui.button_group():
            ui.button("0", on_click=lambda: update_bits_then_submit(bit=False))
            ui.button("1", on_click=lambda: update_bits_then_submit(bit=True))
