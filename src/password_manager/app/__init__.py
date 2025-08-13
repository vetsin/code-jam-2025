"""The application layer.

This module figures out how to tie everything together and export the app.
"""

import logging

from nicegui import Client, app, ui
from nicegui.page_arguments import RouteMatch

from password_manager.backend.database import FileStorage
from password_manager.components.pages import *

logger = logging.getLogger()
storage = FileStorage()


class SubPages(ui.sub_pages):
    def _render_page(self, match: RouteMatch) -> bool:
        if self._is_registering():
            if match.path not in ["/register", "/logout"]:
                self._reset_match()
                ui.navigate.to("/register")
                return True
        if not self._has_vault():
            load_vault_page(storage)
            return True
        if self._has_vault() and not self._is_unlocked():
            unlock_page(storage)
            return True
        logger.debug("Default render path")
        return super()._render_page(match)

    def _render_404(self) -> None:
        with ui.column().classes("absolute-center items-center"):
            ui.icon("error_outline", size="4rem").classes("text-red")
            ui.label("404 - UhOh!").classes("text-2xl text-red")
            ui.label(f'The page "{self._router.current_path}" does not exist.').classes("text-gray-600")
            with ui.row().classes("mt-4"):
                ui.button("Go Home", icon="home", on_click=lambda: ui.navigate.to("/")).props("outline")
                ui.button("Go Back", icon="arrow_back", on_click=ui.navigate.back).props("outline")

    def _render_error(self, error: Exception) -> None:
        with ui.column().classes("absolute-center items-center"):
            ui.icon("error_outline", size="4rem").classes("text-red")
            ui.label("500 - Internal Server Error").classes("text-2xl text-red")
            ui.label(f'The page "{self._router.current_path}" produced an error.').classes("text-gray-600")
            # NOTE: we do not recommend to show exception messages in production (security risk)
            ui.label(str(error)).classes("text-gray-600")
            with ui.row().classes("mt-4"):
                ui.button("Go Home", icon="home", on_click=lambda: ui.navigate.to("/")).props("outline")
                ui.button("Go Back", icon="arrow_back", on_click=ui.navigate.back).props("outline")

    # def _is_route_protected(self, handler: Callable) -> bool:
    #    return getattr(handler, '_is_protected', False)

    def _has_vault(self) -> bool:
        return app.storage.user.get("vault_id", None) is not None

    def _is_unlocked(self) -> bool:
        return app.storage.user.get("vault_secret", None) is not None

    def _is_registering(self) -> bool:
        return app.storage.user.get("is_registering", False) == True


@ui.page("/")
@ui.page("/{_:path}")
def render(client: Client) -> None:
    SubPages(
        {"/": home_page, "/unlock": unlock_page, "/register": create_vault_page, "/logout": clear_vault_session},
        data={"storage": storage},
    )
