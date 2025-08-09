
import logging
from os import path, mkdir
from typing import Generator
from filelock import Timeout, FileLock
from abc import ABC, abstractmethod

from ..util.exceptions import *
from ..components.vault import Vault

logger = logging.getLogger()

class VaultStorage(ABC):
    @abstractmethod
    def read(self, vault_id: str) -> bytes:
      raise NotImplementedError()

    @abstractmethod
    def write(self, vault_id: str, data: bytes):
      raise NotImplementedError()


class FileStorage(VaultStorage):
    def __init__(self, base_path: str='~/.config/password-jam'):
        self._base = path.expanduser(base_path)
        if not path.exists(self._base):
            mkdir(self._base)

    def read(self, vault_id: str) -> bytes:
        try:
            with FileLock(path.join(self._base, f"{vault_id}.lock")):
                with open(path.join(self._base, vault_id), 'rb') as f:
                    return f.read()
        except FileNotFoundError:
            logging.info(f"Vault '{vault_id}' was not found")
            raise VaultReadException("Unable to read vault")
        except Exception as e:
            # TODO: catch why and state so
            raise VaultReadException("Unable to read vault", e)

    def write(self, vault_id: str, data: bytes):
        try:
            with FileLock(path.join(self._base, f"{vault_id}.lock")):
                with open(path.join(self._base, vault_id), 'wb') as f:
                    f.write(data)
        except:
            # TODO: catch why and state so
            raise VaultSaveException("Unable to save vault")


def get_vault_storage() -> Generator[VaultStorage]:
    storage_impl = FileStorage()
    yield storage_impl