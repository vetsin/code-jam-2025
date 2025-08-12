"""The application layer.

This module figures out how to tie everything together and export the app.
"""

import logging

from nicegui import ui

from password_manager.components.credential_submitter.credential_submitter import CredentialSubmitter
from password_manager.components.credential_submitter.password_submitter_wide import PasswordSubmitterWide
from password_manager.components.vault_view.vault_view import VaultView
from password_manager.components.vault import Vault, VaultEntry, VaultKeyValue

TITLE_SECTION_LABEL = "Vault"

mockVault = Vault()
mockEntry = VaultEntry("Mock Entry")
mockKeyValue = VaultKeyValue("Test", 111)
mockEntry.add_key_value(mockKeyValue)
mockVault.add_entry(mockEntry)
from password_manager.types import Passcode

logger = logging.getLogger()


def temp_submit_passcode_check(passcode: Passcode) -> None:
    """Just print out the passcode.

    In the full app, this might hash the passcode, validate against the user,
    and go to the next screen if it validates.
    """
    logger.info(f"we received the passcode {passcode!r}")


@ui.page("/")
def index() -> None:
    """The main ui element representing the entire app."""
    login_container = ui.column().classes("self-center")

    with login_container as app:
        CredentialSubmitter(on_login_submit)
        VaultView(mockVault)
    # return app


def on_login_submit(username: str, passcode: Passcode) -> None:
    print(f"Test on login submit {username}: {passcode}")
