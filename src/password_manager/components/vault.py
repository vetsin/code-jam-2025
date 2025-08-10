import pickle
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from . import crypto


class VaultKeyValue:
    """Represents a key:value pair witin an entry"""

    # we may consider value being an object with *types*, or we may consider VaultKeyValue to be extendable
    # for example we may have 'username' with non-sensitive tr, 'password' with a sensitive str,
    # we may have a x509 private key which is sensitive, or a x509 public key which is not sensitive
    # attachments, etc.
    def __init__(self, key: str, value: Any):
        self._created = datetime.now(UTC)
        self.key: str = key
        self.value: Any = value

    def __eq__(self, other: object) -> bool:
        if not other:
            return False
        if isinstance(other, VaultKeyValue):
            return self.key == other.key
        return self.key == str(other)

    def __hash__(self) -> int:
        return hash(self.id)


class VaultEntry:
    """The entries we store in the vault. It is presumed a VaultItem may have 1..N key:value pairs."""

    def __init__(self, name: str) -> None:
        self.__id = str(uuid4())
        self._created = datetime.now(UTC)
        self._updated = datetime.now(UTC)
        self.name: str = name
        self.key_values = []

    @property
    def id(self) -> str:
        """Unique Id of this entry"""
        return self.__id

    def add_key_value(self, key_value: VaultKeyValue) -> None:
        """Add a key-value pair."""
        self.key_values.append(key_value)
        self._updated = datetime.now(UTC)

    def get_key_value(self, key: str) -> VaultKeyValue:
        """Get a key-value pair."""
        for kv in self.key_values:
            if kv == key:
                return kv
        return None

    def __eq__(self, other: object) -> bool:
        if not other:
            return False
        if isinstance(other, VaultEntry):
            return self.id == other.id
        return self.id == str(other) or self.name == str(other)

    def __hash__(self) -> int:
        return hash(self.id)


class Vault:
    """Represents the database we read and write to."""

    def __init__(self) -> None:
        self.__id = str(uuid4())
        self._created = datetime.now(UTC)
        self.entries: list[VaultEntry] = []
        # static secret given to us by the server, upon creation -- for validating identity
        self.vault_secret: str = None 

    @property
    def id(self) -> str:
        """Unique ID of this vault"""
        return self.__id

    def get_entry(self, name_or_id: str) -> VaultEntry:
        """Get entry"""
        if not name_or_id:
            return None
        for e in self.entries:
            if e == name_or_id:
                return e
        return None

    def add_entry(self, entry: VaultEntry) -> None:
        """Add entry"""
        self.entries.append(entry)

    def has_entry(self, name_or_id: str) -> bool:
        """Does this entry exist?"""
        return name_or_id in self.entries

    def delete_entry(self, vault_entry: str | VaultEntry) -> None:
        """Remove the given entry"""
        self.entries.remove(vault_entry)

    def new_entry(self, entry_name: str, key: str, value: Any) -> VaultEntry:
        """Convinence method to add new entry, must seed with a new key-value"""
        entry = VaultEntry(entry_name)
        entry.add_key_value(VaultKeyValue(key, value))
        self.add_entry(entry)
        return entry

    def __eq__(self, other: object) -> bool:
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


def decrypt_vault(data: bytes, key: crypto.UnlockKey) -> Vault:
    """Given the key, decrypt the bytes into a Vault"""
    decrypted_bytes = crypto.decrypt_data(data, key)
    return pickle.loads(decrypted_bytes)  # noqa: S301


def encrypt_vault(vault: Vault, key: crypto.UnlockKey) -> bytes:
    """Given the key, encrypt the Vault"""
    decrypted_bytes = pickle.dumps(vault)
    return crypto.encrypt_data(decrypted_bytes, key)
