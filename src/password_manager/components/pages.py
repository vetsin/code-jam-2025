import json
import logging
import time
from nicegui import app, ui
from cryptography.exceptions import InvalidSignature

from password_manager.backend.database import SavedLoginInfo, VaultStorage
from password_manager.components.credential_submitter.credential_submitter import CredentialSubmitter
from password_manager.types import Passcode
from password_manager.util import Ref, crypto
from password_manager.util.exceptions import VaultReadError


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


def register_page(storage: VaultStorage) -> None:
    user: Ref[str | None] = Ref(None)
    passcode: Ref[Passcode | None] = Ref(None)

    def cache_credentials(submitted_user: str, submitted_passcode: Passcode) -> None:
        logging.debug(f"we cached the passcode {submitted_passcode!r} for user: {submitted_user}")

        user.inner = submitted_user
        passcode.inner = submitted_passcode

    def try_submit() -> None:
        logging.debug(f"trying to submit user {user} pass {passcode}")

        if user.inner is None or user.inner == "" or passcode.inner is None:
            ui.notify("Enter credentials", type="negative")
            return

        if storage.exists(user.inner):
            ui.notify("Vault already exists", color="negative")
        else:
            try:
                storage.create(user.inner)
                # TODO: we want to embed the password into the vault at this user at this point somehow
                ui.navigate.to("/")
            except:
                ui.notify("fail", color="negative")

    ui.label("Register")
    CredentialSubmitter(on_submit=cache_credentials, submit_text="save")
    ui.button("Use this passcode", on_click=try_submit)

    ui.link("back to login", "/")


def clear_vault_session() -> None:
    app.storage.user["vault_id"] = None
    app.storage.user["vault_data"] = None
    app.storage.user["is_registering"] = None
    app.storage.user.clear()
    ui.navigate.to("/")


def unlock_page(storage: VaultStorage, saved_login_info: SavedLoginInfo) -> None:
    """Create the unlock page. This function is read like a noun.

    Not to be confused with the interior function `try_unlock_vault`, read like a verb.

    args are global state passed in from app.render.
    """

    def try_unlock_vault(saved_login_info: SavedLoginInfo) -> None:
        """Try to unlock the vault using some SavedLoginInfo and go to the vault page if successful. Noop if not."""
        # this should be a match statement but those in python look terrible if
        # we want to look for a some case instead of a none case.
        # I found checking for the data the intuitive way was also somewhat unreadable
        try:
            (ssvault, token) = saved_login_info.get()  # type: ignore
            crypto.decrypt_data(ssvault.vault_data, token.key)  # type: ignore
            ui.navigate.to("/vault")
        except (TypeError, AttributeError, InvalidSignature):
            pass

    try_unlock_vault(saved_login_info)

    def on_submit(user: str, passcode: Passcode) -> None:
        # as a note, we assert saved_login_info.get() is some (ssvault, token) iff token doesn't unlock ssvault.
        # see what happens above.

        # log.
        logging.debug(f"we received the passcode {passcode!r} for user: {user}")

        # build a token from the the given passcode
        encrypted_passcode: crypto.UnlockKey = crypto.SimpleUnlockKey(with_seed=passcode)
        token = crypto.Token(encrypted_passcode, created_on=time.time(), lifetime_in_secs=5 * 60)

        # pull in ssvault from storage only if the user ID provided changed from previous saved_login_info.
        # ie we've cached the ssvault in saved_login_info
        match saved_login_info.get():
            case None:
                try:
                    ssvault = storage.read(vault_id=user)
                except VaultReadError as e:
                    logging.info(f"probably tried to read a user that doesn't exist: {e}")
                    ui.notify("That user doesn't exist.", color="negative")
                    return
            case (ssvault, _):
                ssvault = ssvault

        # update saved_login_info and use it to try to unlock vault
        saved_login_info.set_info(ssvault, token)
        try_unlock_vault(saved_login_info)

    ui.label("Login")
    CredentialSubmitter(on_submit, submit_text="login")
    ui.link("or, register", "/register")


def vault_page() -> None:
    ui.label("ARRIVED AT VAULT!")


def settings_page() -> None:
    ui.label("HERE!")
