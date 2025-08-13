import logging
import secrets
from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path
from pydantic import BaseModel
from cryptography.exceptions import InvalidSignature

from filelock import FileLock

from password_manager.util.crypto import sign_data, validate_signature
from password_manager.util.exceptions import VaultReadError, VaultSaveError, VaultValidationError

logger = logging.getLogger()


class ServerSideVault(BaseModel):
    vault_id: str
    vault_data: bytes
    vault_secret: str


class VaultStorage(ABC):
    """abstract storage method"""

    @abstractmethod
    def read(self, vault_id: str) -> ServerSideVault:
        """Read"""
        raise NotImplementedError

    @abstractmethod
    def write(self, vault_id: str, data: bytes) -> None:
        """Write"""
        raise NotImplementedError

    @abstractmethod
    def create(self, vault_id: str) -> ServerSideVault:
        """create new vault, returning the secret"""
        raise NotImplementedError

    @abstractmethod
    def exists(self, vault_id: str) -> bool:
        """Exists"""
        raise NotImplementedError


class FileStorage(VaultStorage):
    """Just store to filesystem"""

    def __init__(self, base_path: str = "~/.config/password-jam"):
        self._base = Path(base_path).expanduser()
        if not Path.exists(self._base):
            Path.mkdir(self._base)

    def read(self, vault_id: str) -> ServerSideVault:
        """Return the vault, or raise"""
        if not self.exists(vault_id):
            raise VaultReadError("Vault does not exist")
        try:
            with (
                FileLock(self._get_path(f"{vault_id}.lock")),
                Path.open(self._get_path(vault_id), "rb") as f,
                Path.open(self._get_path(f"{vault_id}.secret"), "r") as s,
            ):
                return ServerSideVault(vault_id=vault_id, vault_data=f.read(), vault_secret=s.read())
        except FileNotFoundError as e:
            logger.info("Vault '%s' was not found", vault_id)
            raise VaultReadError("Unable to read vault, not found") from e

    def write(self, vault_id: str, data: bytes) -> None:
        """Write the vault, or raise"""
        if not self.exists(vault_id):
            raise VaultReadError("Vault does not exist, cannot write")
        try:
            # read it first, so we can validate the signature...
            vault = self.read(vault_id)
            data = validate_signature(data, vault.vault_secret.encode("utf-8"))
            with FileLock(self._get_path(f"{vault_id}.lock")), Path.open(self._get_path(vault_id), "wb") as f:
                f.write(data)
        except InvalidSignature as e:
            logger.error("Vault '%s' had an invalid signature when attempting to write", vault_id)
            raise VaultValidationError("Invalid siganture") from e
        except Exception as e:
            # most likely will propagate any exception from self.read(...)
            raise e

    def create(self, vault_id: str) -> ServerSideVault:
        """new vault, will generate a new secret"""
        if self.exists(vault_id):
            raise VaultSaveError("Unable to create vault, already exists") from e
        try:
            with (
                FileLock(self._get_path(f"{vault_id}.lock")),
                Path.open(self._get_path(vault_id), "wb") as f,
                Path.open(self._get_path(f"{vault_id}.secret"), "w") as s,
            ):
                # generate a secret first
                secret = secrets.token_hex(32)
                s.write(secret)

                # now we just sign 'nothing' so we can validate 'nothing'
                f.write(sign_data(b"", secret.encode("utf-8")))
                return ServerSideVault(vault_id=vault_id, vault_data=b"", vault_secret=secret)
        except Exception as e:
            try:
                self._get_path(vault_id).unlink()
                self._get_path(f"{vault_id}.secret").unlink()
            except Exception:
                pass
            logger.error("Unknown and uncaught error writing vault %s", e)
            # raise VaultSaveError("Unable to create vault") from e
            raise e

    def exists(self, path: str) -> bool:
        """if path exists"""
        return self._get_path(path).exists()

    def _get_path(self, path: Path) -> Path:
        """protect against directory traversals, aka ensure we are always under our dir"""
        new_path = (self._base / path).resolve()
        if not new_path.is_relative_to(self._base):
            raise ValueError("Attempted directory traversal likely")
        return new_path.absolute()


def get_vault_storage() -> Generator[VaultStorage]:
    """Get whatever impl we usin"""
    storage_impl = FileStorage()
    yield storage_impl
