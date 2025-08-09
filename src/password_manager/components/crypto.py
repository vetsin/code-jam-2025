import hashlib
from abc import ABC, abstractmethod

from password_manager.util import todo


class UnlockKey(ABC):
    """Abstract base class that defines what an unlock key is."""

    @abstractmethod
    def generate_key(self) -> bytes:
        """Generate a key for unlocking the vault.

        This method should be implemented by subclasses to provide specific key generation logic.
        """
        todo()


class SimpleUnlockKey(UnlockKey):
    """A simple implementation of UnlockKey."""

    def __init__(self, custom_salt: bytes | None = None, person: bytes = b"vault") -> None:
        salt = custom_salt if custom_salt else self.__class__.__name__.encode("utf-8")
        self.__h = hashlib.blake2b(salt=salt[: hashlib.blake2b.SALT_SIZE], person=person)

    def seed(self, seed: str | bytes) -> None:
        """Get seed."""
        seed = seed if isinstance(seed, bytes) else str(seed).encode("utf-8")
        self.__h.update(seed)

    def generate_key(self) -> bytes:
        """Generate key."""
        return self.__h.digest()
