import pytest

from unittest import TestCase
from cryptography.exceptions import InvalidSignature

from password_manager.util import crypto

class TestCrypto(TestCase):
    def test_encrypt_decrypt(self):
        key = crypto.SimpleUnlockKey()
        key.seed(b'some insecure test key')

        assert len(key.generate_key()) == 64, "Key should be specific length"

        plain_data = b'some plaintext to be encrypted decrypted'
        encrypted_data = crypto.encrypt_data(plain_data, key)
        assert plain_data != encrypted_data
        assert b'plaintext' not in encrypted_data

        decrypted_data = crypto.decrypt_data(encrypted_data, key)
        assert plain_data == decrypted_data

    def test_signature(self):
        key = crypto.SimpleUnlockKey()
        key.seed(b'badkey')
        with self.assertRaises(InvalidSignature):
            crypto.decrypt_data(b'whatever'*5, key)

    def test_decrypt(self):
        key = crypto.SimpleUnlockKey()
        key.seed(b'some insecure test key')
        bad_key = crypto.SimpleUnlockKey()
        bad_key.seed(b'whatever')
        encrypted_data = crypto.encrypt_data(b'plaintext', key)
        with self.assertRaises(Exception):
            crypto.decrypt_data(encrypted_data, bad_key)
