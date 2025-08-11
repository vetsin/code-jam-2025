from nicegui import ui
from collections.abc import Callable
from password_manager.components.passcode_factories import ALL_PASSCODE_INPUTS
from password_manager.types import Component, Passcode, PasscodeInput


PASSWORD_SECTION_LABEL = "Password"


class PasswordSubmitterWide(Component):
    def __init__(self, on_set_passcode: Callable[[Passcode], None], submit_text: str):
        self.set_passcode = on_set_passcode
        self.submit_text = submit_text
        self.__make_ui()

    def __make_ui(self) -> None:
        with ui.card():
            ui.label(PASSWORD_SECTION_LABEL)
            tabs = self.__make_password_input_tabs()
            self.__make_tab_contents(tabs)

    def __make_tab_contents(self, tabs: ui.tabs) -> None:
        with ui.tab_panels(tabs, value=ALL_PASSCODE_INPUTS[0].get_name()).classes("w-full"):
            for password_input in ALL_PASSCODE_INPUTS:
                self.__make_tab_content(password_input)

    def __make_tab_content(self, password_input: type[PasscodeInput]) -> None:
        with ui.tab_panel(password_input.get_name()):
            password_input(self.set_passcode, self.submit_text)

    def __make_password_input_tabs(self) -> ui.tabs:
        with ui.tabs().classes("w-full") as tabs:
            for password_input in ALL_PASSCODE_INPUTS:
                ui.tab(password_input.get_name())

        return tabs
