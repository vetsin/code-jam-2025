import hashlib
from abc import ABC, abstractmethod


class UnlockKey(ABC):
    @abstractmethod
    def generate_key(self) -> bytes:
        """Generate a key for unlocking the vault.
        This method should be implemented by subclasses to provide specific key generation logic.
        """


class SimpleUnlockKey(UnlockKey):
    """A simple implementation of UnlockKey"""

    def __init__(self, custom_salt: bytes = None, person: bytes = b"vault"):
        salt = custom_salt if custom_salt else self.__class__.__name__.encode("utf-8")
        self.__h = hashlib.blake2b(salt=salt[: hashlib.blake2b.SALT_SIZE], person=person)

    def seed(self, seed: str | bytes):
        seed = seed if isinstance(seed, bytes) else seed.encode("utf-8")
        self.__h.update(seed)

    def generate_key(self) -> bytes:
        return self.__h.digest()
