import json
import logging
import pickle
from re import U
from typing import Callable

from nicegui import app, ui
from nicegui.events import GenericEventArguments
import platformdirs

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
from password_manager.util.crypto import SimpleUnlockKey, UnlockKey


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

    async def start_registering() -> None:
        app.storage.user["is_registering"] = True
        ui.navigate.to("/register")

    with ui.card().classes("absolute-center items-center"):
        curr_input = ""
        vault_id = (
            ui.input("Vault Identifier", value=app.storage.user.get("vault_id", ""))
            .props("autofocus")
            .on("keydown.enter", try_load)
            .bind_value(globals(), "curr_input")
        )
        with ui.row().classes("mt-4"):
            ui.button("Register", on_click=start_registering).props("outline")
            ui.button("Login", on_click=try_load).props("outline").bind_enabled(globals(), "curr_input")


def create_vault_page(storage: VaultStorage) -> None:
    registration_info = {"vault_id": "", "unlock_key": None}
    if app.storage.user.get("vault_id", None) != None:
        app.storage.user["is_registering"] = False
        ui.navigate.to("/")

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
                # this makes our custom routing in SubPages break
                # app.storage.user["vault_id"] = vid
                # app.storage.user["vault_secret"] = ssv.vault_secret
                ui.navigate.to("/")
            except Exception as e:
                logging.getLogger().debug(e)
                storage.delete(vid)
                ui.notify(f"Failed to create {e}", color="negative")

    def on_passcode_set(p: Passcode) -> None:
        ui.notify(f"updated passcode", type="info")
        registration_info["unlock_key"] = p

    with ui.stepper().props("vertical").classes("absolute-center items-center") as stepper:

        async def stepper_next_if_valid_vid() -> None:
            if storage.exists(registration_info["vault_id"]):
                ui.notify("Vault already exists", color="negative")
            else:
                stepper.next()

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
                ui.button("Next", on_click=stepper_next_if_valid_vid).bind_enabled(registration_info, "vault_id")

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
                ui.button("Create Vault", on_click=try_create).bind_enabled(registration_info, "unlock_key")
                ui.button("Back", on_click=stepper.previous).props("flat")

    # with ui.row().classes("mt-4"):
    #    ui.button("Next", on_click=try_create)


def clear_vault_session() -> None:
    logging.getLogger().debug("entered logout thing")
    app.storage.user["vault_id"] = None
    app.storage.user["vault_data"] = None
    app.storage.user["is_registering"] = None
    app.storage.user.clear()
    (platformdirs.user_cache_path(appname="password-jam", appauthor="password-jam") / "passcode").unlink(
        missing_ok=True
    )

    logging.getLogger().debug(f"app.storage.user {app.storage.user}")
    ui.navigate.to("/load")


def unlock_page(storage: VaultStorage) -> None:
    def temp_submit_passcode_check(p: Passcode) -> None:  # type: ignore
        with open(
            platformdirs.user_cache_path(appname="password-jam", appauthor="password-jam") / "passcode",
            "wb",
        ) as f:
            f.write(p)

        np = crypto.SimpleUnlockKey()
        np.seed(p)
        p: UnlockKey = np

        vault_id = app.storage.user["vault_id"]
        if not vault_id:
            ui.notify("No vault ID set, please load a vault first", color="negative")
            return
        ssv = storage.read(vault_id)
        if not ssv:
            ui.notify("Vault does not exist", color="negative")
            return
        try:
            logging.getLogger().debug("tryna unsign secret")
            unsigned_encrypted_vault = crypto.validate_signature(ssv.vault_data, ssv.vault_secret.encode("utf-8"))
            logging.getLogger().debug("tryna decrypt vault")
            decrypted_vault = vault.decrypt_vault(unsigned_encrypted_vault, p)
            logging.getLogger().debug("success")
        except:
            ui.notify("incorrect passcode", type="negative")
            return
        ui.notify("Vault unlocked successfully", color="positive")
        app.storage.user["vault_secret"] = decrypted_vault.vault_secret
        # THIS FAILS -- need to figure out the data binding stuff for objects
        # in particular, this is the thing that throws TypeError: Type is not JSON serializable: Vault, like, three times
        # without tracing back to this line
        # app.storage.user["vault"] = decrypted_vault

        logging.getLogger().debug("got here whoppee")
        # terrible terrible hack so i can start working on vault rendering
        # just save the decrypted vault to disk
        hackpath = platformdirs.user_cache_path(appname="password-jam", appauthor="password-jam")
        hackpath.mkdir(parents=True, exist_ok=True)
        with open(hackpath / "literally_just_the_decrypted_vault", "wb") as f:
            f.write(pickle.dumps(decrypted_vault))
        logging.getLogger().debug("here 2")
        ui.navigate.to("/")

    with ui.column().classes("absolute-center items-center"):
        CredentialSubmitter(temp_submit_passcode_check)


@protected
def home_page(storage: VaultStorage) -> None:
    # terrible terrible hack so i can start working on vault rendering
    # just load the decrypted vault from disk
    logging.getLogger().debug("got to home page")
    try:
        with open(
            platformdirs.user_cache_path(appname="password-jam", appauthor="password-jam")
            / "literally_just_the_decrypted_vault",
            "rb",
        ) as f:
            my_vault: vault.Vault = pickle.loads(f.read())
    except FileNotFoundError:
        try:
            vault_id = app.storage.user["vault_id"]
            ssv = storage.read(vault_id)
            with open(
                platformdirs.user_cache_path(appname="password-jam", appauthor="password-jam") / "passcode",
                "rb",
            ) as f:
                p = f.read()
            logging.getLogger().debug("tryna unsign secret")
            unsigned_encrypted_vault = crypto.validate_signature(ssv.vault_data, ssv.vault_secret.encode("utf-8"))
            logging.getLogger().debug("tryna decrypt vault")
            key = SimpleUnlockKey()
            key.seed(p)
            my_vault = vault.decrypt_vault(unsigned_encrypted_vault, key)
            logging.getLogger().debug("successfully restored from passcode in storage")
            # TODO whoops realized this whole hack (passcode and literally_just_the_decrypted_vault)
            # could have probably been done properly by just base64 encoding and putting it into nicegui user sstorage.
            # that's how you'd get around bytes and other data notbeing json serializable. base64 is a string, which is.
        except:
            # we're probably not actually routing here to view our vault, bounce to somewhere else.
            ui.navigate.to("/load")
            return
    logging.getLogger().debug("file thing'd")

    # terrible terrible hack so i can start working on vault rendering
    # immediately just clear the decrypted vault from disk
    (
        platformdirs.user_cache_path(appname="password-jam", appauthor="password-jam")
        / "literally_just_the_decrypted_vault"
    ).unlink(missing_ok=True)
    logging.getLogger().debug("file rm thing'd")

    vault_contents = ui.column().classes("absolute-center items-center")

    def save_my_vault_to_storage() -> None:
        key = crypto.SimpleUnlockKey()

        with open(
            platformdirs.user_cache_path(appname="password-jam", appauthor="password-jam") / "passcode",
            "rb",
        ) as f:
            key.seed(f.read())

        encrypted_vault = vault.encrypt_vault(my_vault, key)
        double_signed_vault = crypto.sign_data(encrypted_vault, my_vault.vault_secret.encode("utf-8"))
        storage.write(app.storage.user["vault_id"], double_signed_vault)

    def render_entry(entry: vault.VaultEntry) -> None:
        with vault_contents:
            with ui.row() as row:

                def delete_entry() -> None:
                    row.delete()

                    for i, arbitrary_entry in enumerate(my_vault.entries):
                        if arbitrary_entry.id == entry.id:
                            break
                    my_vault.entries.pop(i)

                    save_my_vault_to_storage()

                ui.label(f"{entry.key_values[0].key}: {entry.key_values[0].value}")
                ui.button(icon="delete", on_click=delete_entry).props("flat size=sm padding=xs")
                ui.button(icon="content_copy", on_click=lambda: ui.clipboard.write(entry.key_values[0].value)).props(
                    "flat size=sm padding=xs"
                )

    def add_entry_helper(label: str, content: str) -> None:
        """
        Add an entry to the vault by
        - adding it to the representation in RAM
        - adding it to the DOM representation
        - encrypt the RAM repr and save to disk
        """
        logging.getLogger().debug("making an entry")

        entry = vault.VaultEntry("")
        entry.add_key_value(vault.VaultKeyValue(label, content))
        my_vault.add_entry(entry)

        render_entry(entry)

        save_my_vault_to_storage()

    with vault_contents:
        ui.link("lock vault", "/logout")
    for entry in my_vault.entries:
        render_entry(entry)

    with vault_contents:
        ui.separator()
        ui_entrylabel = ui.input("label")
        ui_entrycontent = ui.input("content")

    def add_entry_to_vault() -> None:
        # we need this blank function to be here because we want to do this trick where
        # we refer to ui_entrylabel and such in the args. there's a better way i'm sure but i'm tired.
        add_entry_helper(ui_entrylabel.value, ui_entrycontent.value)

    with vault_contents:
        ui.button("new entry", on_click=add_entry_to_vault)
    print("got to end of hm")
