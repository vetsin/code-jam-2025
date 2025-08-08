"""The application layer.

This module figures out how to tie everything together and export the app.
"""

from nicegui import ui

from password_manager.components import login
from password_manager.components.passcode_factories import Passcode


def temp_submit_passcode_check(p: Passcode) -> None:
    """Just print out the passcode.

    In the full app, this might hash the passcode, validate against the user,
    and go to the next screen if it validates.
    """
    print(f"we received the passcode {p}")


def app() -> ui.element:
    """The main ui element representing the entire app."""
    login_container = ui.column().classes("self-center")

    with login_container as app:
        login.login(temp_submit_passcode_check)

    return app
