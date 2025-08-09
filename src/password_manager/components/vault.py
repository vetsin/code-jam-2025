import pickle
from typing import Any
from . import crypto
from time import time

from password_manager.util import todo



class Vault:
    """Represents the database we read and write to."""

    def __init__(self) -> None:
        self.entries: list[VaultEntry] = []

    def unlock(self, key: crypto.UnlockKey) -> None:
        """Unlock the vault."""

    def lock(self) -> None:
        """Lock the vault."""

    def is_unlocked(self) -> bool:
        """Whether the vault is locked."""
        todo()


def decrypt_vault(data: bytes, key: crypto.UnlockKey) -> Vault:
    decrypted_bytes = crypto.decrypt_data(data, key)
    return pickle.load(decrypted_bytes)

def encrypt_vault(vault: Vault, key: crypto.UnlockKey) -> bytes:
    decrypted_bytes = pickle.dumps(vault)
    return crypto.encrypt_data(decrypted_bytes, key)


class VaultKeyValue:
    """Represents a key:value pair witin an entry"""
    # we may consider value being an object with *types*, or we may consider VaultKeyValue to be extendable
    # for example we may have 'username' with non-sensitive tr, 'password' with a sensitive str,
    # we may have a x509 private key which is sensitive, or a x509 public key which is not sensitive
    # attachments, etc.
    def __init__(self, id: int, key: str, value: Any):
        self.id: int = id
        self.key: str = key 
        self.value: Any = value


class VaultEntry:
    """The entries we store in the vault. It is presumed a VaultItem may have 1..N key:value pairs."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.key_values = []

    def add_key_value(self, key_value: VaultKeyValue) -> None:
        """Add a key-value pair."""

    def get_key_value(self, _key: Any) -> None:
        """Get a key-value pair."""
