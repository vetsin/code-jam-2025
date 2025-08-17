import json
import logging
from typing import Callable

from nicegui import app, ui
from nicegui.events import GenericEventArguments

from password_manager.backend import vault
from password_manager.backend.database import VaultStorage
from password_manager.components.credential_submitter.credential_submitter import CredentialSubmitter
from password_manager.components.credential_submitter.password_submitter_dropdown import (
    PasswordSubmitterDropdown,
    PasscodeItem,
)
from password_manager.components.passcode_factories import ALL_PASSCODE_INPUTS
from password_manager.types import Passcode, PasscodeInput
from password_manager.util import crypto
from password_manager.util.crypto import UnlockKey


logger = logging.Logger("pages", level=logging.DEBUG)


def protected(func: Callable) -> Callable:
    """Decorator to mark a route handler as requiring authentication for the custom_sub_pages."""
    func._is_protected = True  # pylint: disable=protected-access
    return func


def load_vault_page(storage: VaultStorage) -> None:
    async def try_load() -> None:
        if storage.exists(str(vault_id.value)):
            app.storage.user["vault_id"] = str(vault_id.value)
            ui.navigate.to("/unlock")
        else:
            ui.notify("Vault does not exist", color="negative")

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


def create_vault_page(storage: VaultStorage) -> None:
    if app.storage.user.get("vault_id", None) != None:
        app.storage.user["is_registering"] = False
        ui.navigate.to("/")
    registration_info = {"vault_id": "", "unlock_key": None}

    async def try_create() -> None:
        vid = str(registration_info["vault_id"]).strip()
        if storage.exists(vid):
            ui.notify("Vault already exists", color="negative")
        elif registration_info.get("unlock_key", None) is None:
            ui.notify("Please set a passcode", color="negative")
        else:
            try:
                # todo: move this out
                ssv = storage.create(vid)
                # just make a new vault with the given secret...
                new_vault = vault.Vault()
                new_vault.vault_secret = ssv.vault_secret
                # TODO: have the lockers return a VaultKey not bytes
                key = crypto.SimpleUnlockKey()
                key.seed(registration_info["unlock_key"])
                encrypted_vault = vault.encrypt_vault(new_vault, key)

                vault.decrypt_vault(encrypted_vault, key)  # will throw if we failed somewhere

                double_signed_vault = crypto.sign_data(encrypted_vault, new_vault.vault_secret.encode("utf-8"))
                storage.write(vid, double_signed_vault)
                app.storage.user["vault_id"] = vid
                app.storage.user["vault_secret"] = ssv.vault_secret
                ui.navigate.to("/")
            except Exception as e:
                print(e)
                storage.delete(vid)
                ui.notify(f"Failed to create {e}", color="negative")

    def on_passcode_set(p: Passcode) -> None:
        registration_info["unlock_key"] = p

    with ui.card().classes("absolute-center items-center"):
        with ui.stepper().props("vertical").classes("w-full") as stepper:

            def set_div_to_unlocker(event: GenericEventArguments) -> None:
                passcode_div.clear()
                with passcode_div:
                    event.value(on_passcode_set, "Set Passcode")

            with ui.step("Step 1: Vault Identifier"):
                ui.label("Set a unique identifier for your vault:")
                (
                    ui.input("Vault Identifier", value=app.storage.user.get("vault_id", ""))
                    .props("autofocus")
                    .bind_value_to(registration_info, "vault_id")
                )
                with ui.stepper_navigation():
                    ui.button("Next", on_click=stepper.next).bind_enabled(registration_info, "vault_id")

            with ui.step("Step 2: Vault Unlock Method"):
                ui.label("Choose how you want to unlock your vault:")
                ui.select({x: x.get_name() for x in ALL_PASSCODE_INPUTS}).on_value_change(set_div_to_unlocker)
                with ui.stepper_navigation():
                    ui.button("Next", on_click=stepper.next)
                    ui.button("Back", on_click=stepper.previous).props("flat")

            with ui.step("Step 3: Set Passcode") as step3:
                ui.label("Set your passcode:")
                passcode_div = ui.element("div")
                with ui.stepper_navigation():
                    ui.button("Create Vault", on_click=try_create)
                    ui.button("Back", on_click=stepper.previous).props("flat")

        # with ui.row().classes("mt-4"):
        #    ui.button("Next", on_click=try_create)


def clear_vault_session() -> None:
    app.storage.user["vault_id"] = None
    app.storage.user["vault_data"] = None
    app.storage.user["is_registering"] = None
    app.storage.user.clear()
    ui.navigate.to("/")


def unlock_page(storage: VaultStorage) -> None:
    def temp_submit_passcode_check(p: Passcode | UnlockKey) -> None:
        if type(p) == Passcode or type(p) == bytes:
            np = crypto.SimpleUnlockKey()
            np.seed(p)
            p = np

        vault_id = app.storage.user["vault_id"]
        if not vault_id:
            ui.notify("No vault ID set, please load a vault first", color="negative")
            return
        ssv = storage.read(vault_id)
        if not ssv:
            ui.notify("Vault does not exist", color="negative")
            return
        unsigned_encrypted_vault = crypto.validate_signature(ssv.vault_data, ssv.vault_secret.encode("utf-8"))
        decrypted_vault = vault.decrypt_vault(unsigned_encrypted_vault, p)
        ui.notify("Vault unlocked successfully", color="positive")
        app.storage.user["vault_secret"] = decrypted_vault.vault_secret
        # THIS FAILS -- need to figure out the data binding stuff for objects
        app.storage.user["vault"] = decrypted_vault
        ui.navigate.to("/")

    with ui.column().classes("self-center"):
        CredentialSubmitter(temp_submit_passcode_check)


@protected
def home_page(storage: VaultStorage) -> None:
    ui.markdown(f"""
    hello world we would vault stuff here\n
                """)
