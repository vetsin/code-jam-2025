from collections.abc import Callable
from dataclasses import dataclass
from password_manager.components.login import login
from password_manager.components.passcode_factories import Passcode
from password_manager.components.PasscodeInput import PasscodeInput
from nicegui import ui

SUBMIT_BUTTON_TEXT = "Login | Register"
TITLE_SECTION_LABEL = "Login / Register"
USERNAME_SECTION_LABEL = "Username"
USERNAME_SECTION_PLACEHOLDER = "username"
ERROR_MESSAGE_ON_NULL_USERNAME = "Please enter a valid username"
ERROR_MESSAGE_ON_NULL_PASSCODE = "Please set a passcode"


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

            PasscodeInput(self.__set_passcode)

            self.submit_button = ui.button(SUBMIT_BUTTON_TEXT, on_click=self.__on_submit)


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
