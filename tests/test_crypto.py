"""
Family Voice Shield (FVS) - Unit and Parity Test Suite for Phase 1 Crypto Core
"""

import json
import os
import unittest
from pathlib import Path

from core.crypto import (
    LockoutSession,
    VerificationResult,
    derive_directional_keys,
    derive_duress_key,
    hkdf_sha256,
    hotp,
    hotp_bin,
    totp,
    totp_words,
    verify_numeric,
    verify_words,
)
from core.wordlist import WORDS, bin_to_words, words_to_bin, index_to_word, word_to_index


class TestCryptoCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture_path = Path(__file__).parent / "fixtures" / "crypto_test_vectors.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            cls.fixtures = json.load(f)

    def test_rfc4226_hotp_vectors(self):
        """Verify 100% compliance with RFC 4226 test vectors (counter 0 to 9)."""
        data = self.fixtures["rfc4226_hotp"]
        key = data["key_ascii"].encode("ascii")

        for item in data["vectors"]:
            counter = item["counter"]
            expected = item["hotp"]
            actual = hotp(key, counter, digits=6)
            self.assertEqual(
                actual,
                expected,
                f"HOTP mismatch at counter {counter}: expected {expected}, got {actual}",
            )

    def test_rfc6238_totp_vectors(self):
        """Verify 100% compliance with RFC 6238 test vectors (6 and 8 digits)."""
        data = self.fixtures["rfc6238_totp_sha1"]
        key = data["key_ascii"].encode("ascii")
        step = data["step_seconds"]
        t0 = data["t0"]

        for item in data["vectors"]:
            t = item["time"]
            exp_6 = item["totp_6"]
            exp_8 = item["totp_8"]

            act_6 = totp(key, t, step=step, t0=t0, digits=6)
            act_8 = totp(key, t, step=step, t0=t0, digits=8)

            self.assertEqual(act_6, exp_6, f"TOTP 6-digit mismatch at t={t}")
            self.assertEqual(act_8, exp_8, f"TOTP 8-digit mismatch at t={t}")

    def test_hkdf_directional_derivation(self):
        """Verify HKDF-SHA256 directional derivation and asymmetry."""
        data = self.fixtures["directional_hkdf"]
        k_pair = bytes.fromhex(data["k_pair_hex"])

        k_a_to_b, k_b_to_a = derive_directional_keys(k_pair)

        # Both keys must be 20 bytes
        self.assertEqual(len(k_a_to_b), 20)
        self.assertEqual(len(k_b_to_a), 20)

        # Crucial security property: directional keys MUST be different
        self.assertNotEqual(k_a_to_b, k_b_to_a)

        # Directional keys must generate different TOTP codes at same time
        timestamp = 1700000000
        code_a = totp(k_a_to_b, timestamp)
        code_b = totp(k_b_to_a, timestamp)
        self.assertNotEqual(code_a, code_b)

    def test_duress_key_derivation(self):
        """Verify duress key is distinct and generates valid secondary codes."""
        k_pair = bytes.fromhex("11" * 20)
        k_a_to_b, _ = derive_directional_keys(k_pair)
        k_duress = derive_duress_key(k_a_to_b)

        self.assertEqual(len(k_duress), 20)
        self.assertNotEqual(k_a_to_b, k_duress)

        timestamp = 1700000030
        normal_code = totp(k_a_to_b, timestamp)
        duress_code = totp(k_duress, timestamp)
        self.assertNotEqual(normal_code, duress_code)

    def test_wordlist_encoding_and_decoding(self):
        """Verify 2,048-word list encoding and 22-bit round trip."""
        self.assertEqual(len(WORDS), 2048)

        for item in self.fixtures["word_encoding"]:
            bin_val = item["bin"]
            exp_w1, exp_w2 = item["words"]
            w1, w2 = bin_to_words(bin_val)
            self.assertEqual((w1, w2), (exp_w1, exp_w2))
            decoded_bin = words_to_bin(w1, w2)
            self.assertEqual(decoded_bin, bin_val)

        # Roundtrip across sample values
        for test_val in [0, 1, 42, 2047, 2048, 50000, 1048575, 4194303]:
            w1, w2 = bin_to_words(test_val)
            self.assertEqual(words_to_bin(w1, w2), test_val)

    def test_verification_window_and_clock_skew(self):
        """Verify tolerance for clock skew with configurable window."""
        key = b"test_secret_key_1234"
        now = 1700000000
        step = 30

        code_current = totp(key, now, step=step)
        code_prev = totp(key, now - step, step=step)
        code_next = totp(key, now + step, step=step)
        code_far = totp(key, now - (step * 2), step=step)

        # Window = 1 accepts previous, current, and next
        self.assertTrue(verify_numeric(key, code_current, now, step=step, window=1))
        self.assertTrue(verify_numeric(key, code_prev, now, step=step, window=1))
        self.assertTrue(verify_numeric(key, code_next, now, step=step, window=1))

        # Window = 1 rejects 2 steps away
        self.assertFalse(verify_numeric(key, code_far, now, step=step, window=1))

        # Window = 0 only accepts current
        self.assertTrue(verify_numeric(key, code_current, now, step=step, window=0))
        self.assertFalse(verify_numeric(key, code_prev, now, step=step, window=0))

    def test_lockout_session_state_machine(self):
        """Verify fail-closed lockout policy: 3 failed attempts lock out session."""
        key = b"session_secret_key_12"
        session = LockoutSession(key, max_attempts=3)
        now = 1700000000

        valid_code = totp(key, now)
        duress_key = derive_duress_key(key)
        duress_code = totp(duress_key, now)

        # Attempt 1: wrong code -> INVALID
        res1 = session.check_numeric("000000" if valid_code != "000000" else "111111", now)
        self.assertEqual(res1, VerificationResult.INVALID)
        self.assertEqual(session.failed_attempts, 1)
        self.assertFalse(session.is_locked)

        # Attempt 2: wrong code -> INVALID
        res2 = session.check_numeric("222222", now)
        self.assertEqual(res2, VerificationResult.INVALID)
        self.assertEqual(session.failed_attempts, 2)
        self.assertFalse(session.is_locked)

        # Attempt 3: wrong code -> LOCKED_OUT
        res3 = session.check_numeric("333333", now)
        self.assertEqual(res3, VerificationResult.LOCKED_OUT)
        self.assertEqual(session.failed_attempts, 3)
        self.assertTrue(session.is_locked)

        # Attempt 4: even a CORRECT code is now rejected because session is locked
        res4 = session.check_numeric(valid_code, now)
        self.assertEqual(res4, VerificationResult.LOCKED_OUT)

        # Reset session allows re-verification
        session.reset()
        self.assertFalse(session.is_locked)
        self.assertEqual(session.failed_attempts, 0)
        res_after_reset = session.check_numeric(valid_code, now)
        self.assertEqual(res_after_reset, VerificationResult.SUCCESS)

    def test_lockout_session_duress_detection(self):
        """Verify duress code triggers DURESS status without locking out immediately."""
        key = b"duress_test_key_12345"
        session = LockoutSession(key, max_attempts=3)
        now = 1700000000

        duress_key = derive_duress_key(key)
        duress_code = totp(duress_key, now)

        result = session.check_numeric(duress_code, now)
        self.assertEqual(result, VerificationResult.DURESS)
        self.assertTrue(session.is_verified)
        self.assertFalse(session.is_locked)

    def test_parity_1000_vectors(self):
        """Deterministic parity test verifying 1,000 generated (key, time) pairs."""
        # Using a deterministic pseudo-random sequence (Linear Congruential Generator)
        seed = 123456789
        for i in range(1000):
            seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
            key = f"key_{seed}_{i}".encode("utf-8")
            time_val = 1700000000 + (seed % 1000000)

            # Generate numeric and words
            code = totp(key, time_val)
            w1, w2 = totp_words(key, time_val)

            # Assert numeric format
            self.assertEqual(len(code), 6)
            self.assertTrue(code.isdigit())

            # Assert words in lexicon
            self.assertIn(w1, WORDS)
            self.assertIn(w2, WORDS)

            # Verification round-trip
            self.assertTrue(verify_numeric(key, code, time_val))
            self.assertTrue(verify_words(key, (w1, w2), time_val))


if __name__ == "__main__":
    unittest.main()
