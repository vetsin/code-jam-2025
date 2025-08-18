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
        return app.storage.user.get("vault_secret", None) is not None

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
    # TypeError: Object of type Vault is not JSON serializable, on reload after unlocking vault
    with ui.header().classes("item-center"):
        ui.markdown(f"debugging header: `app.storage.user={json.dumps(app.storage.user)}`")
