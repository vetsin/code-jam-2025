from nicegui import ui
from collections.abc import Callable
from password_manager.components.passcode_factories import Passcode

from password_manager.components.passcode_factories.anagram import anagraminput_factory
from password_manager.components.passcode_factories.binary import binaryinput_factory
from password_manager.components.passcode_factories.map import map_input_factory
from password_manager.components.passcode_factories.text import textinput_factory
from password_manager.components.passcode_factories.typst import typstinput_factory

PASSWORD_SECTION_LABEL = "Password"

PASSWORD_INPUTS = (
    ("Anagram", anagraminput_factory),
    ("Binary", binaryinput_factory),
    ("Map", map_input_factory),
    ("Text", textinput_factory),
    ("Typst", typstinput_factory),
)

class PasscodeInput:
    def __init__(self, set_passcode: Callable[[str, Passcode], None]):
        self.set_passcode = set_passcode
        self.__make_ui()

    def __make_ui(self) -> None:
        with ui.card():
            ui.label(PASSWORD_SECTION_LABEL)
            tabs = self.__make_password_input_tabs()
            self.__make_tab_contents(tabs)

    def __make_tab_contents(self, tabs: list[ui.tab]) -> None:
        with ui.tab_panels(tabs, value=PASSWORD_INPUTS[0][0]).classes("w-full"):
            for password_input in PASSWORD_INPUTS:
                self.__make_tab_content(password_input)

    def __make_tab_content(self, password_input: tuple[str, Callable]) -> None:
        with ui.tab_panel(password_input[0]):
            password_input[1](self.set_passcode)

    def __make_password_input_tabs(self) -> list[ui.tab]:
        with ui.tabs().classes("w-full") as tabs:
            for password_input in PASSWORD_INPUTS:
                ui.tab(password_input[0])

        return tabs
