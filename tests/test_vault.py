from unittest import TestCase
from cryptography.exceptions import InvalidSignature

from password_manager.backend import vault
from password_manager.util import crypto

class TestVault(TestCase):
    def test_basic(self):
        v = vault.Vault()
        self.assertEqual(len(v.entries), 0)
        test_entry = v.new_entry("test entry", "myKey", "myValue")
        self.assertEqual(test_entry.name, "test entry")
        self.assertIsNotNone(test_entry.key_values)
        self.assertEqual(len(test_entry.key_values), 1)

        self.assertEqual(len(v.entries), 1)

        self.assertIsNotNone(v.get_entry("test entry"))
        self.assertIsNotNone(v.get_entry(test_entry))
        self.assertIsNotNone(v.get_entry(test_entry.id))

        v.delete_entry(test_entry)
        self.assertEqual(len(v.entries), 0)

    def test_encrypt_decrypt(self):
      key = crypto.SimpleUnlockKey()
      key.seed(b'some insecure test key')

      v = vault.Vault()
      test_entry = v.new_entry("test entry", "myKey", "myValue")
      test_entry_id = test_entry.id

      encrypted = vault.encrypt_vault(v, key)
      self.assertIsNotNone(encrypted)

      decrypted_v = vault.decrypt_vault(encrypted, key)
      self.assertIsNotNone(decrypted_v)
      self.assertEqual(v, decrypted_v)

      decrypted_entry = decrypted_v.get_entry("test entry")
      self.assertEqual(test_entry, decrypted_entry)
      decrypted_kv = decrypted_entry.get_key_value("myKey")
      self.assertEqual(decrypted_kv.value, "myValue")
