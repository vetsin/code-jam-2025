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
PASSWORD_INPUT_DROPDOWN_LABEL = "Select Password Input Type"

PASSWORD_INPUTS = (
    ("Anagram", anagraminput_factory),
    ("Binary", binaryinput_factory),
    ("Map", map_input_factory),
    ("Text", textinput_factory),
    ("Typst", typstinput_factory),
)

class LoginRegister:
    def __init__(self):
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
                    on_change=lambda e: self.__set_username(e.value)
                )

            self.__make_password_input_section()

            self.submit_button = ui.button(SUBMIT_BUTTON_TEXT, on_click=self.__on_submit)

    def __make_password_input_section(self) -> None:
        with ui.card():
            ui.label(PASSWORD_SECTION_LABEL)

            tab_options = []
            with ui.tabs().classes('w-full') as tabs:
                for password_input in PASSWORD_INPUTS:
                    tab_options.append(ui.tab(password_input[0]))

            with ui.tab_panels(tabs, value=tab_options[0]).classes('w-full'):
                for i, tab_option in enumerate(tab_options):
                    with ui.tab_panel(tab_option):
                        PASSWORD_INPUTS[i][1](self.__set_passcode)
    
    def __set_username(self, new_username: str) -> None:
        """ This exists because the ui was being buggy with assignment in a lambda """
        self.username = new_username
        
    def __set_passcode(self, new_passcode: Passcode) -> None:
        self.passcode = new_passcode

    def __on_submit(self) -> None:
        print(f"User logged in with USERNAME: {self.username}, PASSCODE: {self.passcode}")
