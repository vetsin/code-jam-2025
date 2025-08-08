class VaultDatabase:

    def load_vault(self, vault_id: str) -> bytes:
        raise NotImplementedError("This method should be implemented by subclasses.")

    def save_vault(self, vault_id: str, vault_data: bytes) -> None:
        raise NotImplementedError("This method should be implemented by subclasses.")
