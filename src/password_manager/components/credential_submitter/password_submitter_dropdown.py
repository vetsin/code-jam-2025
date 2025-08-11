from collections.abc import Callable

from nicegui import ui

from password_manager.components.passcode_factories import ALL_PASSCODE_INPUTS
from password_manager.types import Component, Passcode, PasscodeInput


class PasscodeItem(Component):
    def __init__(
        self,
        passcode_input: type[PasscodeInput],
        on_submit: Callable[[Passcode], None],
        submit_text: str,
        passcode_input_parent: ui.element,
    ):
        """Spawn a named item representing a passcode input.

        It creates a new passcode input in `passcode_input_parent` on select.
        """

        def spawn_passcode_into_dropdown() -> None:
            """Spawn the passcode into the given parent, wrapped in a closable card."""
            with (
                passcode_input_parent,
                ui.card() as card,
                ui.row().classes("w-full justify-between items-center mb-2"),
            ):
                passcode_input(on_submit, submit_text)
                ui.button(icon="close", on_click=lambda: card.delete()).props("flat round size=sm").classes(
                    "text-gray-500 hover:text-gray-700",
                )

        ui.item(passcode_input.get_name(), on_click=spawn_passcode_into_dropdown)


class PasswordSubmitterDropdown(Component):
    def __init__(self, on_submit: Callable[[Passcode], None], submit_text: str) -> None:
        with ui.column() as login, ui.dropdown_button("passcode type", auto_close=True) as _dropdown:
            for passcode_input in ALL_PASSCODE_INPUTS:
                PasscodeItem(
                    passcode_input,
                    on_submit,
                    submit_text,
                    passcode_input_parent=login,
                )
