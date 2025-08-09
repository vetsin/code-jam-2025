import hashlib
import os
from abc import ABC, abstractmethod

from password_manager.util import todo
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class UnlockKey(ABC):
    """Abstract base class that defines what an unlock key is."""

    @abstractmethod
    def generate_key(self) -> bytes:
        """Generate a key for unlocking the vault.

        This method should be implemented by subclasses to provide specific key generation logic.
        """
        todo()


class SimpleUnlockKey(UnlockKey):
    """A 'simple' implementation of UnlockKey."""

    def __init__(self, custom_salt: bytes | None = None, person: bytes = b"vault") -> None:
        self._salt = custom_salt if custom_salt else self.__class__.__name__.encode("utf-8")
        self.__h = hashlib.blake2b(salt=self._salt[: hashlib.blake2b.SALT_SIZE], person=person)

    def seed(self, seed: str | bytes) -> None:
        """Get seed."""
        if not seed:
            raise ValueError('cannot seed with nothing')
        seed = seed if isinstance(seed, bytes) else str(seed).encode("utf-8")
        self.__h.update(seed)

    def generate_key(self) -> bytes:
        """Generate key, should be 512 bits"""
        return self.__h.digest()


def encrypt_data(data: bytes, key: UnlockKey):
    k1 = key.generate_key()
    assert len(k1) > 32, "we require at least 256 bits for a key"
    k2 = k1[:len(k1)//2] # we use this part to sign
    k3 = k1[len(k1)//2:]
    iv = os.urandom(16)
    encrypted = iv + aes_encrypt(iv, data, k3)
    return sign_data(encrypted, k2)

def decrypt_data(data: bytes, key: UnlockKey):
    k1 = key.generate_key()
    assert len(k1) > 32, "we require at least 256 bits for a key"
    k2 = k1[:len(k1)//2] # we use this part to sign
    k3 = k1[len(k1)//2:]
    data = validate_signature(data, k2)
    iv = data[:16]
    return aes_decrypt(iv, data[16:], k3)

def aes_encrypt(iv: bytes, data: bytes, key: bytes):
    assert len(key) == 32, f"got {len(key)}"
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return encrypted_data

def aes_decrypt(iv: bytes, data: bytes, key: bytes):
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(data) + decryptor.finalize()
    return decrypted_data

def sign_data(data: bytes, key: bytes):
    h = HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    signature = h.finalize() # should be 32 bytes, when using sha256
    return signature + data

def validate_signature(data: bytes, key: bytes):
    h = HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data[32:])
    # https://cryptography.io/en/latest/hazmat/primitives/mac/hmac/#cryptography.hazmat.primitives.hmac.HMAC.verify
    # should raise if invalid
    h.verify(data[:32])
    return data[32:]
