from collections.abc import Callable
from dataclasses import dataclass
from password_manager.components.passcode_factories import Passcode, PasscodeInputFactory
from password_manager.components.login import login
from nicegui import ui
from password_manager.components.passcode_factories.anagram import anagraminput_factory
from password_manager.components.passcode_factories.binary import binaryinput_factory
from password_manager.components.passcode_factories.map import map_input_factory
from password_manager.components.passcode_factories.text import textinput_factory
from password_manager.components.passcode_factories.typst import typstinput_factory

SUBMIT_BUTTON_TEXT = "Login | Register"
TITLE_SECTION_LABEL = "Login / Register"
USERNAME_SECTION_LABEL = "Username"
USERNAME_SECTION_PLACEHOLDER = "username"
PASSWORD_SECTION_LABEL = "Password"
ERROR_MESSAGE_ON_NULL_USERNAME = "Please enter a valid username"
ERROR_MESSAGE_ON_NULL_PASSCODE = "Please set a passcode"

PASSWORD_INPUTS = (
    ("Anagram", anagraminput_factory),
    ("Binary", binaryinput_factory),
    ("Map", map_input_factory),
    ("Text", textinput_factory),
    ("Typst", typstinput_factory),
)


class LoginRegister:
    def __init__(self, submit_login: Callable[[str, Passcode], None]):
        self.submit_login = submit_login

        self.username = ""
        self.passcode = None
        self.__make_ui()

    def __make_ui(self) -> None:
        with ui.card():
            ui.label(TITLE_SECTION_LABEL)

            with ui.card():
                ui.input(
                    label=USERNAME_SECTION_LABEL,
                    placeholder=USERNAME_SECTION_PLACEHOLDER,
                    on_change=lambda e: self.__set_username(e.value),
                )

            self.__make_password_input_section()

            self.submit_button = ui.button(SUBMIT_BUTTON_TEXT, on_click=self.__on_submit)

    def __make_password_input_section(self) -> None:
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
            password_input[1](self.__set_passcode)

    def __make_password_input_tabs(self) -> list[ui.tab]:
        with ui.tabs().classes("w-full") as tabs:
            for password_input in PASSWORD_INPUTS:
                ui.tab(password_input[0])

        return tabs

    def __set_username(self, new_username: str) -> None:
        """This exists because the ui was being buggy with assignment in a lambda."""
        self.username = new_username

    def __set_passcode(self, new_passcode: Passcode) -> None:
        """This exists to work with the factory system."""
        self.passcode = new_passcode

    def __on_submit(self) -> None:
        if not self.username:
            ui.notify(ERROR_MESSAGE_ON_NULL_USERNAME, color="negative")
            return

        if self.passcode == None:
            ui.notify(ERROR_MESSAGE_ON_NULL_PASSCODE, color="negative")
            return

        self.submit_login(self.username, self.passcode)
