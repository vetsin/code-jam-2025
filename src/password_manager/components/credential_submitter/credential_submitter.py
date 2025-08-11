from collections.abc import Callable
from password_manager.components.credential_submitter.password_submitter_dropdown import password_submitter_dropdown
from password_manager.components.credential_submitter.password_submitter_wide import PasswordSubmitterWide
from password_manager.components.passcode_factories import Passcode
from nicegui import ui

SUBMIT_BUTTON_TEXT = "Login | Register"
TITLE_SECTION_LABEL = "Login / Register"
USERNAME_SECTION_LABEL = "Username"
USERNAME_SECTION_PLACEHOLDER = "username"
ERROR_MESSAGE_ON_NULL_USERNAME = "Please enter a valid username"
ERROR_MESSAGE_ON_NULL_PASSCODE = "Please set a passcode"


class CredentialSubmitter:
    def __init__(self, submit_login: Callable[[str, Passcode], None]):
        self.submit_login = submit_login

        self.username = ""

        self.__make_ui()

    def __make_ui(self) -> None:
        with ui.card():
            ui.label(TITLE_SECTION_LABEL)
            self.__make_username_input_card()
            # password_submitter_dropdown(self.__try_submit)
            PasswordSubmitterWide(on_set_passcode=self.__try_submit)

    def __make_username_input_card(self) -> None:
        with ui.card():
            ui.input(
                label=USERNAME_SECTION_LABEL,
                placeholder=USERNAME_SECTION_PLACEHOLDER,
                on_change=lambda e: self.__set_username(e.value),
            )

    def __set_username(self, new_username: str) -> None:
        """This exists because can't do assignment in a lambda."""
        self.username = new_username

    def __try_submit(self, p: Passcode) -> None:
        if not self.username:
            ui.notify(ERROR_MESSAGE_ON_NULL_USERNAME, color="negative")
            return

        self.submit_login(self.username, p)
