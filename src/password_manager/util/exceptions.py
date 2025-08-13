class VaultReadError(Exception):
    """Failure to read a vault."""


class VaultSaveError(Exception):
    """Failure to save a vault."""


class VaultValidationError(Exception):
    """Signature related issue."""
