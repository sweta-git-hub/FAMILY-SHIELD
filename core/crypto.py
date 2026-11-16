"""
Family Voice Shield (FVS) - Core Cryptographic Library
Pure-function, zero-IO cryptographic routines for:
- HOTP (RFC 4226)
- TOTP (RFC 6238)
- HKDF-SHA256 directional key derivation (RFC 5869)
- Word-list phonetic code encoding/decoding (2,048-word lexicon)
- Verification window and fail-closed lockout state machine
- Duress code derivation and verification
"""

import hashlib
import hmac
import math
import struct
from enum import Enum
from typing import Optional, Tuple, Union

from core.wordlist import bin_to_words, words_to_bin, index_to_word, word_to_index


class VerificationResult(str, Enum):
    SUCCESS = "SUCCESS"
    DURESS = "DURESS"
    INVALID = "INVALID"
    LOCKED_OUT = "LOCKED_OUT"


def hkdf_extract(salt: Optional[bytes], ikm: bytes) -> bytes:
    """HKDF-Extract per RFC 5869 using SHA-256."""
    if salt is None or len(salt) == 0:
        salt = bytes([0] * 32)
    return hmac.new(salt, ikm, hashlib.sha256).digest()


def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    """HKDF-Expand per RFC 5869 using SHA-256."""
    hash_len = 32
    if length > 255 * hash_len:
        raise ValueError("Cannot expand to more than 255 * HashLen bytes")

    n = math.ceil(length / hash_len)
    okm = b""
    t = b""
    for i in range(1, n + 1):
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    return okm[:length]


def hkdf_sha256(ikm: bytes, salt: Optional[bytes] = None, info: bytes = b"", length: int = 20) -> bytes:
    """HKDF-SHA256 (Extract and Expand) returning requested key bytes."""
    prk = hkdf_extract(salt, ikm)
    return hkdf_expand(prk, info, length)


def derive_directional_keys(k_pair: bytes) -> Tuple[bytes, bytes]:
    """
    Derive distinct directional keys:
    K_A_to_B: A (Member/Child) proves identity to B (Guardian/Parent)
    K_B_to_A: B proves identity to A
    Prevents live relay / reflection attacks.
    """
    k_a_to_b = hkdf_sha256(k_pair, salt=None, info=b"FVS1|A->B", length=20)
    k_b_to_a = hkdf_sha256(k_pair, salt=None, info=b"FVS1|B->A", length=20)
    return k_a_to_b, k_b_to_a


def derive_duress_key(k_dir: bytes) -> bytes:
    """
    Derive duress key from directional key:
    Generates a valid-looking second TOTP code for the same time step
    that silently flags duress / coercion.
    """
    return hkdf_sha256(k_dir, salt=None, info=b"FVS1|DURESS", length=20)


def hotp_bin(key: bytes, counter: int) -> int:
    """
    Computes 31-bit dynamically truncated binary integer per RFC 4226.
    """
    counter_bytes = struct.pack(">Q", counter)
    mac = hmac.new(key, counter_bytes, hashlib.sha1).digest()
    offset = mac[19] & 0x0F
    bin_code = (
        ((mac[offset] & 0x7F) << 24)
        | ((mac[offset + 1] & 0xFF) << 16)
        | ((mac[offset + 2] & 0xFF) << 8)
        | (mac[offset + 3] & 0xFF)
    )
    return bin_code


def hotp(key: bytes, counter: int, digits: int = 6) -> str:
    """Computes HOTP code string per RFC 4226."""
    bin_code = hotp_bin(key, counter)
    code = bin_code % (10 ** digits)
    return f"{code:0{digits}d}"


def totp_counter(timestamp: int, step: int = 30, t0: int = 0) -> int:
    """Computes counter for a given unix timestamp and time step."""
    return (timestamp - t0) // step


def totp(key: bytes, timestamp: int, step: int = 30, t0: int = 0, digits: int = 6) -> str:
    """Computes TOTP numeric code per RFC 6238."""
    counter = totp_counter(timestamp, step, t0)
    return hotp(key, counter, digits=digits)


def totp_words(key: bytes, timestamp: int, step: int = 30, t0: int = 0) -> Tuple[str, str]:
    """Computes TOTP 2-word phonetic code from 2,048-word lexicon."""
    counter = totp_counter(timestamp, step, t0)
    bin_code = hotp_bin(key, counter)
    return bin_to_words(bin_code)


def verify_numeric(
    key: bytes,
    candidate: str,
    timestamp: int,
    step: int = 30,
    t0: int = 0,
    digits: int = 6,
    window: int = 1,
) -> bool:
    """
    Verify a candidate numeric TOTP code within [-window, +window] time steps.
    Constant-time string comparison.
    """
    cleaned = candidate.strip()
    if len(cleaned) != digits or not cleaned.isdigit():
        return False

    center = totp_counter(timestamp, step, t0)
    for delta in range(-window, window + 1):
        expected = hotp(key, center + delta, digits=digits)
        if hmac.compare_digest(cleaned, expected):
            return True
    return False


def verify_words(
    key: bytes,
    candidate: Tuple[str, str],
    timestamp: int,
    step: int = 30,
    t0: int = 0,
    window: int = 1,
) -> bool:
    """
    Verify candidate 2-word code within [-window, +window] time steps.
    """
    try:
        cand_w1 = candidate[0].strip().lower()
        cand_w2 = candidate[1].strip().lower()
    except (IndexError, AttributeError):
        return False

    center = totp_counter(timestamp, step, t0)
    for delta in range(-window, window + 1):
        exp_w1, exp_w2 = bin_to_words(hotp_bin(key, center + delta))
        if exp_w1 == cand_w1 and exp_w2 == cand_w2:
            return True
    return False


class LockoutSession:
    """
    Fail-closed challenge verification session state machine.
    Tracks attempts, handles normal vs duress codes, enforces 3-strike lockout.
    """

    MAX_ATTEMPTS = 3

    def __init__(self, key_dir: bytes, max_attempts: int = MAX_ATTEMPTS):
        self.key_dir = key_dir
        self.key_duress = derive_duress_key(key_dir)
        self.max_attempts = max_attempts
        self.failed_attempts = 0
        self.is_locked = False
        self.is_verified = False

    def check_numeric(
        self,
        candidate: str,
        timestamp: int,
        step: int = 30,
        t0: int = 0,
        digits: int = 6,
        window: int = 1,
    ) -> VerificationResult:
        """Verify numeric candidate with lockout state enforcement."""
        if self.is_locked:
            return VerificationResult.LOCKED_OUT

        # Check duress code first
        if verify_numeric(self.key_duress, candidate, timestamp, step, t0, digits, window):
            self.is_verified = True
            return VerificationResult.DURESS

        # Check primary directional key
        if verify_numeric(self.key_dir, candidate, timestamp, step, t0, digits, window):
            self.is_verified = True
            return VerificationResult.SUCCESS

        # Verification failed
        self.failed_attempts += 1
        if self.failed_attempts >= self.max_attempts:
            self.is_locked = True
            return VerificationResult.LOCKED_OUT
        return VerificationResult.INVALID

    def check_words(
        self,
        candidate: Tuple[str, str],
        timestamp: int,
        step: int = 30,
        t0: int = 0,
        window: int = 1,
    ) -> VerificationResult:
        """Verify words candidate with lockout state enforcement."""
        if self.is_locked:
            return VerificationResult.LOCKED_OUT

        # Check duress
        if verify_words(self.key_duress, candidate, timestamp, step, t0, window):
            self.is_verified = True
            return VerificationResult.DURESS

        # Check primary key
        if verify_words(self.key_dir, candidate, timestamp, step, t0, window):
            self.is_verified = True
            return VerificationResult.SUCCESS

        self.failed_attempts += 1
        if self.failed_attempts >= self.max_attempts:
            self.is_locked = True
            return VerificationResult.LOCKED_OUT
        return VerificationResult.INVALID

    def reset(self) -> None:
        """Explicit session reset (e.g., when a new legitimate call starts)."""
        self.failed_attempts = 0
        self.is_locked = False
        self.is_verified = False
