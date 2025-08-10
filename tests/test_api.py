from unittest import TestCase
from fastapi.testclient import TestClient

import main
from password_manager.backend.database import get_vault_storage
from password_manager.components import crypto, vault

class TestAPI(TestCase):
    def setUp(self):
        self.client = TestClient(main.fastapi_app)

    def test_health(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status':'ok'})

    def test_bad_read(self):
        response = self.client.get('/api/vaults/non-existant-vault')
        self.assertEqual(response.status_code, 404)

    def test_bad_write(self):
        response = self.client.patch('/api/vaults/non-existant-vault', content=b'blabla')
        self.assertEqual(response.status_code, 404)

    def test_create_then_manage(self):
        # first make sure it doesn't exist...
        response = self.client.get('/api/vaults/test-vault')
        self.assertEqual(response.status_code, 404)

        try:
            # create it...
            response = self.client.post('/api/vaults/test-vault')
            self.assertEqual(response.status_code, 201)
            body = response.json()
            self.assertIsNotNone(body)
            self.assertTrue(body.get('vault_id'), 'test-vault')
            secret = body.get('vault_secret')
            self.assertEqual(len(secret), 64)

            # validate it's on disk...
            base = next(get_vault_storage())._base
            self.assertTrue(base.exists())
            self.assertTrue((base / "test-vault").exists())
            self.assertTrue((base / "test-vault.secret").exists())

            # validate we can read it now....
            response = self.client.get('/api/vaults/test-vault')
            self.assertEqual(response.status_code, 200)
            # we want to be sure we have no secret in our response...
            self.assertFalse(secret in response.text)

            # validate we can save it now...
            key = crypto.SimpleUnlockKey()
            key.seed(b'some insecure test key')
            v = vault.Vault()
            v.vault_secret = secret

            encrypted = vault.encrypt_vault(v, key)
            double_signed_vault = crypto.sign_data(encrypted, v.vault_secret.encode('utf-8'))
            response = self.client.patch('/api/vaults/test-vault', content=double_signed_vault)
            self.assertEqual(response.status_code, 200)

            # now try it with a bad key
            response = self.client.patch('/api/vaults/test-vault', content=encrypted)
            self.assertEqual(response.status_code, 401)

        finally:
            # delete our test files now...
            try:
                (base / "test-vault").unlink()
                (base / "test-vault.secret").unlink()
            except:
                pass





    


