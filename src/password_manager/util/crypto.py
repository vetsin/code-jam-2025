from dataclasses import dataclass
import hashlib
import os
from abc import ABC, abstractmethod
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.hmac import HMAC


class UnlockKey(ABC):
    """Abstract base class that defines what an unlock key is."""

    @abstractmethod
    def generate_key(self) -> bytes:
        """Generate a key for unlocking the vault.

        This method should be implemented by subclasses to provide specific key generation logic.
        """
        raise NotImplementedError("needs an impl")


class SimpleUnlockKey(UnlockKey):
    """A 'simple' implementation of UnlockKey."""

    def __init__(
        self,
        custom_salt: bytes | None = None,
        person: bytes = b"vault",
        with_seed: bytes | None = None,
    ) -> None:
        self._salt = custom_salt if custom_salt else self.__class__.__name__.encode("utf-8")
        self.__h = hashlib.blake2b(salt=self._salt[: hashlib.blake2b.SALT_SIZE], person=person)
        if with_seed:
            self.seed(with_seed)

    def seed(self, seed: str | bytes) -> None:
        """Get seed."""
        if not seed:
            raise ValueError("cannot seed with nothing")
        seed = seed if isinstance(seed, bytes) else seed.encode("utf-8")  # type: ignore # type checker too dumb
        self.__h.update(seed)

    def generate_key(self) -> bytes:
        """Generate key, should be 512 bits"""
        return self.__h.digest()


@dataclass
class Token:
    key: UnlockKey
    created_on: float  # epoch in seconds, from time.time()
    lifetime_in_secs: float  # marked for deletion after this number of seconds

    def should_invalidate(self) -> bool:
        """Return whether we should invalidate this token because it's too old.

        Invalidation must be done by its owner. That's `SavedLoginInfo` right now.
        """
        return time.time() - self.created_on > self.lifetime_in_secs


def encrypt_data(data: bytes, key: UnlockKey) -> bytes:
    """Encrypt and sign data using key.

    The result will be [signature][iv][data].
    """
    k1 = key.generate_key()
    if len(k1) < 32:
        raise ValueError("we require at least 256 bits for a key")
    k2 = k1[: len(k1) // 2]  # we use this part to sign
    k3 = k1[len(k1) // 2 :]
    iv = os.urandom(16)
    encrypted = iv + aes_encrypt(iv, data, k3)
    return sign_data(encrypted, k2)


def decrypt_data(data: bytes, key: UnlockKey) -> bytes:
    """Validate signature and decrypt data using key.

    The data is expected will be [signature][iv][data].

    :raises: cryptography.exceptions.InvalidSignature
    """
    k1 = key.generate_key()
    if len(k1) < 32:
        raise ValueError("we require at least 256 bits for a key")
    k2 = k1[: len(k1) // 2]  # we use this part to sign
    k3 = k1[len(k1) // 2 :]
    data = validate_signature(data, k2)
    iv = data[:16]
    return aes_decrypt(iv, data[16:], k3)


def aes_encrypt(iv: bytes, data: bytes, key: bytes) -> bytes:
    """Standard aes encryption"""
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize()


def aes_decrypt(iv: bytes, data: bytes, key: bytes) -> bytes:
    """Standard aes decryption"""
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(data) + decryptor.finalize()


def sign_data(data: bytes, key: bytes) -> bytes:
    """sha256 hmac, returns [signature][data]"""
    h = HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    signature = h.finalize()  # should be 32 bytes, when using sha256
    return signature + data


def validate_signature(data: bytes, key: bytes) -> bytes:
    """
    Validates the signature, and returns just the data (removes the signature)

    :raises: cryptography.exceptions.InvalidSignature
    """
    h = HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data[32:])
    # https://cryptography.io/en/latest/hazmat/primitives/mac/hmac/#cryptography.hazmat.primitives.hmac.HMAC.verify
    # should raise if invalid
    h.verify(data[:32])
    return data[32:]
