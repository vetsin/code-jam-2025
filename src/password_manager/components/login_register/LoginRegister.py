from collections.abc import Callable
from password_manager.components.passcode_factories import Passcode, PasscodeInputFactory
from password_manager.components.login import login
from nicegui import ui

SUBMIT_BUTTON_TEXT = "Login | Register"
TITLE_SECTION_LABEL = "Login / Register"
USERNAME_SECTION_LABEL = "Username"
USERNAME_SECTION_PLACEHOLDER = "username"
PASSWORD_SECTION_LABEL = "Password"

class LoginRegister:
    def __init__(self, submit_passcode: Callable[[Passcode], None]):
        self.submit_passcode = submit_passcode
        self.username = ""

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

            with ui.card():
                ui.label(PASSWORD_SECTION_LABEL)
                self.passcode_input = login(self.submit_passcode)

            self.submit_button = ui.button(SUBMIT_BUTTON_TEXT, on_click=self.__on_submit)
    
    def __set_username(self, new_username: str) -> None:
        """ This exists because the ui was being buggy with assignment in a lambda """
        self.username = new_username

    def __on_submit(self) -> None:
        print(f"User logged in with USERNAME: {self.username}")
