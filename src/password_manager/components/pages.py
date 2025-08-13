import json
import logging
from nicegui import app, ui

from password_manager.backend.database import VaultStorage
from password_manager.components.credential_submitter.credential_submitter import CredentialSubmitter
from password_manager.components.passcode_factories import Passcode

logger = logging.Logger("pages")


def load_vault_page(storage: VaultStorage) -> None:
    async def try_load() -> None:
        if storage.exists(str(vault_id.value)):
            app.storage.user["vault_id"] = str(vault_id.value)
            ui.navigate.to("/unlock")

    async def try_create() -> None:
        if storage.exists(str(vault_id.value)):
            ui.notify("Vault already exists", color="negative")
        else:
            app.storage.user["is_registering"] = True
            ui.navigate.to("/register")

    with ui.card().classes("absolute-center items-center"):
        vault_id = (
            ui.input("Vault Identifier", value=app.storage.user.get("vault_id", ""))
            .props("autofocus")
            .on("keydown.enter", try_load)
        )
        with ui.row().classes("mt-4"):
            ui.button("Register", on_click=try_create).props("outline")
            ui.button("Login", on_click=try_load).props("outline")
    ui.markdown(f"```{json.dumps(app.storage.user)}```")


def create_vault_page(storage: VaultStorage) -> None:
    if app.storage.user.get("vault_id", None) != None:
        app.storage.user["is_registering"] = False
        ui.navigate.to("/")

    async def try_create() -> None:
        vid = str(vault_id.value)
        if storage.exists(vid):
            ui.notify("Vault already exists", color="negative")
        else:
            try:
                storage.create(vid)
                app.storage.user["vault_id"] = vid
                app.storage.user["is_registering"] = False
                ui.navigate.to("/")
            except:
                ui.notify("fail", color="negative")

    with ui.card().classes("absolute-center items-center"):
        vault_id = (
            ui.input("Vault Identifier", value=app.storage.user.get("vault_id", ""))
            .props("autofocus")
            .on("keydown.enter", try_create)
        )
        with ui.row().classes("mt-4"):
            ui.button("Create", on_click=try_create)


def clear_vault_session() -> None:
    app.storage.user["vault_id"] = None
    app.storage.user["vault_data"] = None
    app.storage.user["is_registering"] = None
    app.storage.user.clear()
    ui.navigate.to("/")


def unlock_page(storage: VaultStorage) -> None:
    def temp_submit_passcode_check(p: Passcode) -> None:
        logger.info(f"we received the passcode {p!r}")

    with ui.column().classes("self-center"):
        CredentialSubmitter(temp_submit_passcode_check)
    ui.markdown(f"""```{json.dumps(app.storage.user)}```""")


def home_page(storage: VaultStorage) -> None:
    clear_vault_session()
    ui.markdown(f"""
    hello world we would vault stuff here\n
    ```{json.dumps(app.storage.user)}```
                """)
