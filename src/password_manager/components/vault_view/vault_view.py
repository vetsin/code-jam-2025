from nicegui import ui
from password_manager.types import Component
from password_manager.components.vault import Vault, VaultEntry, VaultKeyValue

TITLE_SECTION_LABEL = "Vault"


class VaultView(Component):
    def __init__(self, vault: Vault):
        self.vault = vault
        self.__make_ui()

    def __make_ui(self) -> None:
        with ui.card():
            ui.label(TITLE_SECTION_LABEL)
            for entry in self.vault.entries:
                self.__make_vault_entry_card(entry)

    def __make_vault_entry_card(self, vault_entry: VaultEntry) -> None:
        with ui.card().tight():
            ui.label(vault_entry.name)
            with ui.card_section():
                self.__make_vault_entry_key_list(vault_entry.key_values)

    def __make_vault_entry_key_list(self, key_values: list[VaultKeyValue]) -> None:
        with ui.list().props("bordered separator"):
            for key in key_values:
                ui.item(f"key: {key.key} | value: {key.value}")
