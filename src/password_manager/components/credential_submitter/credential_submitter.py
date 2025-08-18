from collections.abc import Callable
from password_manager.components.credential_submitter.password_submitter_dropdown import PasswordSubmitterDropdown
from nicegui import ui

from password_manager.types import Component, Passcode
from password_manager.util.crypto import UnlockKey


TITLE_SECTION_LABEL = "Login"


class CredentialSubmitter(Component):
    def __init__(self, on_submit: Callable[[Passcode | UnlockKey], None]):
        with ui.card():
            ui.label(TITLE_SECTION_LABEL)
            PasswordSubmitterDropdown(on_submit, submit_text="Log in")
