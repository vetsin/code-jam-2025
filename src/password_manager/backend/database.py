
import logging
from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path

from filelock import FileLock

from password_manager.util.exceptions import VaultReadError, VaultSaveError

logger = logging.getLogger()

class VaultStorage(ABC):
    """abstract storage method"""

    @abstractmethod
    def read(self, vault_id: str) -> bytes:
      """Read"""
      raise NotImplementedError

    @abstractmethod
    def write(self, vault_id: str, data: bytes) -> None:
      """Write"""
      raise NotImplementedError


class FileStorage(VaultStorage):
    """Just store to filesystem"""

    def __init__(self, base_path: str="~/.config/password-jam"):
        self._base = Path(base_path).expanduser()
        if not Path.exists(self._base):
            Path.mkdir(self._base)

    def read(self, vault_id: str) -> bytes:
        """Return the vault, or raise"""
        try:
            with FileLock(self._base / f"{vault_id}.lock"):
                with Path.open(self._base / vault_id, "rb") as f:
                    return f.read()
        except FileNotFoundError as e:
            logger.info("Vault '%s' was not found", vault_id)
            raise VaultReadError("Unable to read vault") from e
        except Exception as e:
            # TODO: catch why and state so
            raise VaultReadError("Unable to read vault", e) from e

    def write(self, vault_id: str, data: bytes) -> None:
        """Write the vault, or raise"""
        try:
            with FileLock(self._base / f"{vault_id}.lock"):
                with Path.open(self._base / vault_id, "wb") as f:
                    f.write(data)
        except Exception as e:
            # TODO: catch why and state so
            raise VaultSaveError("Unable to save vault") from e


def get_vault_storage() -> Generator[VaultStorage]:
    """Get whatever impl we usin"""
    storage_impl = FileStorage()
    yield storage_impl
