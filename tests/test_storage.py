"""
Unit tests for Secure Local Vault in Family Voice Shield.
Tests persistence, relationship retrieval, revocation, encrypted export/import,
and tamper-evident HMAC integrity verification.
"""

import unittest

from core.pairing import DeviceRole, PairingSession
from core.storage import SecureVault, SecurityIntegrityError


class TestSecureVault(unittest.TestCase):
    def setUp(self):
        self.vault = SecureVault(master_passphrase="test_secure_passphrase_123")
        self.guardian_phone = "+919876500001"
        self.member_phone = "+919876500002"

        invitation_uri, _ = PairingSession.create_invitation(
            creator_phone=self.guardian_phone,
            creator_role=DeviceRole.GUARDIAN,
            target_phone=self.member_phone,
            target_name="Rahul (Son)",
            step_seconds=60,
        )
        self.guardian_rel, self.member_rel = PairingSession.accept_invitation(
            invitation_uri=invitation_uri,
            acceptor_phone=self.member_phone,
            acceptor_name="Mom",
        )

    def test_add_and_retrieve_relationship(self):
        self.vault.add_relationship(self.guardian_rel)
        retrieved = self.vault.get_relationship(self.guardian_rel.pair_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.peer_name, "Rahul (Son)")
        self.assertEqual(retrieved.peer_phone, self.member_phone)
        self.assertEqual(retrieved.step_seconds, 60)

    def test_retrieve_by_peer_phone(self):
        self.vault.add_relationship(self.guardian_rel)
        # Lookup using non-normalized input format
        found = self.vault.get_by_peer_phone("98765 00002")
        self.assertIsNotNone(found)
        self.assertEqual(found.peer_phone, self.member_phone)

    def test_revocation(self):
        self.vault.add_relationship(self.guardian_rel)
        self.assertEqual(len(self.vault.list_active()), 1)

        # Revoke
        success = self.vault.revoke(self.guardian_rel.pair_id)
        self.assertTrue(success)
        self.assertEqual(len(self.vault.list_active()), 0)
        self.assertEqual(len(self.vault.list_all()), 1)

        # Revoked item cannot generate or verify codes
        with self.assertRaises(ValueError):
            self.guardian_rel.get_outbound_code()

    def test_encrypted_export_and_import(self):
        self.vault.add_relationship(self.guardian_rel)
        exported_envelope = self.vault.export_encrypted_json()

        # Import into fresh vault instance with identical passphrase
        new_vault = SecureVault(master_passphrase="test_secure_passphrase_123")
        new_vault.import_encrypted_json(exported_envelope)

        restored = new_vault.get_relationship(self.guardian_rel.pair_id)
        self.assertIsNotNone(restored)
        self.assertEqual(restored.k_pair, self.guardian_rel.k_pair)
        self.assertEqual(restored.k_outbound, self.guardian_rel.k_outbound)
        self.assertEqual(restored.k_inbound, self.guardian_rel.k_inbound)

    def test_tamper_fails_closed(self):
        import json
        self.vault.add_relationship(self.guardian_rel)
        exported_envelope = self.vault.export_encrypted_json()

        # Attacker modifies the signature or base64 payload
        envelope_data = json.loads(exported_envelope)
        # Flip characters in the base64 payload
        tampered_payload = envelope_data["payload"][:-4] + "XYZQ"
        envelope_data["payload"] = tampered_payload
        tampered_envelope = json.dumps(envelope_data)

        new_vault = SecureVault(master_passphrase="test_secure_passphrase_123")
        with self.assertRaises(SecurityIntegrityError):
            new_vault.import_encrypted_json(tampered_envelope)


if __name__ == "__main__":
    unittest.main()
