from typing import Any

from crypto import UnlockKey

from password_manager.util import todo


class Vault:
    """Represents the database we read and write to."""

    def __init__(self, vault: bytes) -> None:
        pass

    def unlock(self, key: UnlockKey) -> None:
        """Unlock the vault."""

    def lock(self) -> None:
        """Lock the vault."""

    def is_unlocked(self) -> bool:
        """Whether the vault is locked."""
        todo()


class VaultKeyValue:
    """Represents a single entry in the password vault."""

    def __init__(self, key: Any, value: Any) -> None:
        # we may consider value being an object with *types*, or we may consider VaultKeyValue to be extendable
        # for example we may have 'username' with non-sensitive tr, 'password' with a sensitive str,
        # we may have a x509 private key which is sensitive, or a x509 public key which is not sensitive
        # attachments, etc.
        self.key = key
        self.value = value


class VaultEntry:
    """The entries we store in the vault. It is presumed a VaultItem may have 1..N key:value pairs."""

    def __init__(self, name: Any) -> None:
        self.name = name

    def add_key_value(self, key_value: VaultKeyValue) -> None:
        """Add a key-value pair."""

    def get_key_value(self, _key: Any) -> None:
        """Get a key-value pair."""
