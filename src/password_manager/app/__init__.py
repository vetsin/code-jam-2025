"""The application layer.

This module figures out how to tie everything together and export the app.
"""

import logging
from typing import Callable

from nicegui import Client, app, ui
from nicegui.page_arguments import RouteMatch

from password_manager.backend.database import FileStorage
from password_manager.components.pages import *

logger = logging.getLogger()
storage = FileStorage()


class SubPages(ui.sub_pages):
    def _render_page(self, match: RouteMatch) -> bool:
        # this if basically says "if we went to "/" and user storage [vault_secret] is None"
        print(f"going to {match.builder}")
        print(
            f"self._is_route_protected(match.builder) {self._is_route_protected(match.builder)} self._is_unlocked() {self._is_unlocked()}"
        )
        if self._is_route_protected(match.builder) and not self._is_unlocked():
            self._reset_match()
            ui.navigate.to("/load")
            return True
        return super()._render_page(match)

    def _is_route_protected(self, handler: Callable) -> bool:
        return getattr(handler, "_is_protected", False)

    def _has_vault(self) -> bool:
        return app.storage.user.get("vault_id", None) is not None

    def _is_unlocked(self) -> bool:
        # edit: accomodate the terrible hack
        try:
            with open(
                platformdirs.user_cache_path(appname="password-jam", appauthor="password-jam") / "passcode",
                "rb",
            ) as f:
                return (
                    len(f.read(2)) > 0
                )  # if we read a few chars from the terrible hack, and the password is there, we're unlocked
        except FileNotFoundError:
            return False

    # def _is_registering(self) -> bool:
    #    return app.storage.user.get("is_registering", False) == True


@ui.page("/")
@ui.page("/{_:path}")
def render(client: Client) -> None:
    # https://nicegui.io/documentation/sub_pages
    SubPages(
        {
            "/": home_page,
            "/load": load_vault_page,
            "/unlock": unlock_page,
            "/register": create_vault_page,
            "/logout": clear_vault_session,
        },
        data={"storage": storage},
    )
