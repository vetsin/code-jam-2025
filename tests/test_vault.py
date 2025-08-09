import pytest

from unittest import TestCase
from cryptography.exceptions import InvalidSignature
from password_manager.components import crypto, vault

class TestVault(TestCase):
    def test_basic(self):
        v = vault.Vault()
      
    def test_encrypt_decrypt(self):
      key = crypto.SimpleUnlockKey()
      key.seed(b'some insecure test key')

      v = vault.Vault()

      encrypted = vault.encrypt_vault(v, key)
