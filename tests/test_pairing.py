"""
Unit tests for Phone Utility and Pairing Protocol in Family Voice Shield.
Tests E.164 normalization, zero-knowledge pairing exchange, directional isolation,
and live 60-second synchronized code agreement.
"""

import time
import unittest

from core.crypto import LockoutSession, VerificationResult
from core.pairing import (
    DEFAULT_CODE_STEP,
    DeviceRole,
    PairedRelationship,
    PairingSession,
)
from core.phone_util import (
    ContactProfile,
    format_phone_display,
    normalize_phone_number,
)


class TestPhoneUtil(unittest.TestCase):
    def test_normalize_indian_domestic_numbers(self):
        # 10 digits domestic
        self.assertEqual(normalize_phone_number("9876543210"), "+919876543210")
        # With spaces and hyphens
        self.assertEqual(normalize_phone_number(" 98765-43210 "), "+919876543210")
        # With leading 0 (STD)
        self.assertEqual(normalize_phone_number("09876543210"), "+919876543210")
        # With +91 already
        self.assertEqual(normalize_phone_number("+91 98765 43210"), "+919876543210")
        # With 00 international prefix
        self.assertEqual(normalize_phone_number("00919876543210"), "+919876543210")

    def test_normalize_international_numbers(self):
        # US number
        self.assertEqual(normalize_phone_number("+1 (555) 123-4567"), "+15551234567")
        # UK number
        self.assertEqual(normalize_phone_number("+44 20 7946 0991"), "+442079460991")

    def test_normalize_invalid_numbers_raise_error(self):
        with self.assertRaises(ValueError):
            normalize_phone_number("")
        with self.assertRaises(ValueError):
            normalize_phone_number("abc")
        with self.assertRaises(ValueError):
            normalize_phone_number("+123")  # Too short (< 7 digits)
        with self.assertRaises(ValueError):
            normalize_phone_number("+123456789012345678")  # Too long (> 15 digits)

    def test_format_phone_display(self):
        self.assertEqual(format_phone_display("+919876543210"), "+91 98765 43210")
        self.assertEqual(format_phone_display("+15551234567"), "+1 (555) 123-4567")

    def test_contact_profile_validation(self):
        contact = ContactProfile(
            phone="+919876543210",
            name="Rahul (Son)",
            relationship="Child",
        )
        self.assertEqual(contact.name, "Rahul (Son)")
        self.assertEqual(contact.phone, "+919876543210")

        with self.assertRaises(ValueError):
            ContactProfile(phone="invalid_phone", name="Rahul")
        with self.assertRaises(ValueError):
            ContactProfile(phone="+919876543210", name="   ")


class TestPairingProtocol(unittest.TestCase):
    def setUp(self):
        self.guardian_phone = "+919876500001"
        self.member_phone = "+919876500002"
        self.step = 60  # 60 seconds rotation

    def test_create_and_accept_invitation(self):
        # Guardian creates invitation targeted for Member
        invitation_uri, k_pair = PairingSession.create_invitation(
            creator_phone=self.guardian_phone,
            creator_role=DeviceRole.GUARDIAN,
            target_phone=self.member_phone,
            target_name="Rahul (Son)",
            step_seconds=self.step,
        )

        self.assertTrue(invitation_uri.startswith("fvs://pair?"))
        self.assertEqual(len(k_pair), 20)

        # Member accepts invitation
        guardian_rel, member_rel = PairingSession.accept_invitation(
            invitation_uri=invitation_uri,
            acceptor_phone=self.member_phone,
            acceptor_name="Mom",
        )

        self.assertEqual(guardian_rel.role, DeviceRole.GUARDIAN)
        self.assertEqual(member_rel.role, DeviceRole.MEMBER)
        self.assertEqual(guardian_rel.step_seconds, 60)
        self.assertEqual(member_rel.step_seconds, 60)

    def test_invitation_rejects_wrong_acceptor_phone(self):
        invitation_uri, _ = PairingSession.create_invitation(
            creator_phone=self.guardian_phone,
            creator_role=DeviceRole.GUARDIAN,
            target_phone=self.member_phone,
            target_name="Rahul",
        )

        # Attacker tries to accept invitation meant for someone else
        attacker_phone = "+919999999999"
        with self.assertRaises(ValueError):
            PairingSession.accept_invitation(
                invitation_uri=invitation_uri,
                acceptor_phone=attacker_phone,
                acceptor_name="Attacker",
            )

    def test_synchronized_60s_codes_match_perfectly(self):
        invitation_uri, _ = PairingSession.create_invitation(
            creator_phone=self.guardian_phone,
            creator_role=DeviceRole.GUARDIAN,
            target_phone=self.member_phone,
            target_name="Rahul (Son)",
            step_seconds=self.step,
        )
        guardian_rel, member_rel = PairingSession.accept_invitation(
            invitation_uri=invitation_uri,
            acceptor_phone=self.member_phone,
            acceptor_name="Mom",
        )

        fixed_time = 1773750000  # Fixed deterministic timestamp

        # Case 1: Member calls Guardian -> Rahul gives code to Mom
        rahul_outbound_code, rahul_rem = member_rel.get_outbound_code(timestamp=fixed_time)
        mom_expected_code, mom_rem = guardian_rel.get_expected_inbound_code(timestamp=fixed_time)

        # They MUST match identically!
        self.assertEqual(rahul_outbound_code, mom_expected_code)
        self.assertEqual(len(rahul_outbound_code), 6)
        self.assertTrue(rahul_outbound_code.isdigit())
        self.assertEqual(rahul_rem, mom_rem)

        # Verification by Guardian must succeed
        result = guardian_rel.verify_incoming_code(
            candidate_code=rahul_outbound_code, timestamp=fixed_time
        )
        self.assertEqual(result, VerificationResult.SUCCESS)

    def test_directional_isolation_security(self):
        """
        Critical security test:
        Rahul's code to Mom MUST NOT match Mom's code to Rahul!
        This proves directional keys prevent relay reflection attacks.
        """
        invitation_uri, _ = PairingSession.create_invitation(
            creator_phone=self.guardian_phone,
            creator_role=DeviceRole.GUARDIAN,
            target_phone=self.member_phone,
            target_name="Rahul (Son)",
            step_seconds=self.step,
        )
        guardian_rel, member_rel = PairingSession.accept_invitation(
            invitation_uri=invitation_uri,
            acceptor_phone=self.member_phone,
            acceptor_name="Mom",
        )

        fixed_time = 1773750000
        rahul_calling_mom_code, _ = member_rel.get_outbound_code(timestamp=fixed_time)
        mom_calling_rahul_code, _ = guardian_rel.get_outbound_code(timestamp=fixed_time)

        # Directional keys ensure these two codes are DIFFERENT!
        self.assertNotEqual(
            rahul_calling_mom_code,
            mom_calling_rahul_code,
            "Security vulnerability: Directional codes must never be symmetric!",
        )

        # If a scammer attempts to recite Mom's outbound code back to Mom, it fails!
        result = guardian_rel.verify_incoming_code(
            candidate_code=mom_calling_rahul_code, timestamp=fixed_time
        )
        self.assertEqual(result, VerificationResult.INVALID)

    def test_verification_lockout_after_three_failures(self):
        invitation_uri, _ = PairingSession.create_invitation(
            creator_phone=self.guardian_phone,
            creator_role=DeviceRole.GUARDIAN,
            target_phone=self.member_phone,
            target_name="Rahul (Son)",
            step_seconds=self.step,
        )
        guardian_rel, _ = PairingSession.accept_invitation(
            invitation_uri=invitation_uri,
            acceptor_phone=self.member_phone,
            acceptor_name="Mom",
        )

        session = guardian_rel.create_lockout_session(max_attempts=3)
        fixed_time = 1773750000

        # Attempt 1: wrong
        r1 = guardian_rel.verify_incoming_code("000000", timestamp=fixed_time, session=session)
        self.assertEqual(r1, VerificationResult.INVALID)

        # Attempt 2: wrong
        r2 = guardian_rel.verify_incoming_code("111111", timestamp=fixed_time, session=session)
        self.assertEqual(r2, VerificationResult.INVALID)

        # Attempt 3: wrong -> triggers LOCKOUT
        r3 = guardian_rel.verify_incoming_code("222222", timestamp=fixed_time, session=session)
        self.assertEqual(r3, VerificationResult.LOCKED_OUT)

        # Attempt 4: even correct code is locked out (fail-closed!)
        valid_code, _ = guardian_rel.get_expected_inbound_code(timestamp=fixed_time)
        r4 = guardian_rel.verify_incoming_code(valid_code, timestamp=fixed_time, session=session)
        self.assertEqual(r4, VerificationResult.LOCKED_OUT)


if __name__ == "__main__":
    unittest.main()
