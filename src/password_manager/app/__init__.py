"""The application layer.

This module figures out how to tie everything together and export the app.
"""

import logging


from nicegui import Client, app, ui, html
from nicegui.page_arguments import RouteMatch

from password_manager.backend.database import FileStorage, SavedLoginInfo
from password_manager.components.pages import *

logger = logging.getLogger()
storage = FileStorage()


@ui.page("/")
def render(client: Client) -> None:
    # https://nicegui.io/documentation/sub_pages
    with ui.header().classes("item-center"):
        ui.markdown(f"debugging header: `app.storage.user={json.dumps(app.storage.user)}`")

    ui.sub_pages(
        {
            "/": unlock_page,
            "/register": register_page,
            "/vault": vault_page,
            "/vault/settings": settings_page,
        },
        data={
            "storage": storage,
            # fill this on login, remove on invalidate (happens automatically with get()) or vault lock.
            # this is to prevent the user needing to log in a bajillion times, for UX.
            "saved_login_info": SavedLoginInfo(None),
        },
    ).classes("w-96 shrink-0 mx-auto items-center")
