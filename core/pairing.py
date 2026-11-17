"""
Family Voice Shield (FVS) - Pairing Protocol
Handles secure zero-knowledge pairing between family members based on phone numbers.
Derives directional keys (HKDF-SHA256) and generates synchronized 60-second 6-digit codes.
"""

import base64
import os
import time
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from core.crypto import (
    derive_directional_keys,
    derive_duress_key,
    totp,
    verify_numeric,
    LockoutSession,
    VerificationResult,
)
from core.phone_util import normalize_phone_number


DEFAULT_CODE_STEP = 60  # 1 minute (60 seconds) rotation per ADR-006 & user decision


class DeviceRole(str, Enum):
    GUARDIAN = "GUARDIAN"  # Parent / Senior (primarily verifies incoming calls)
    MEMBER = "MEMBER"      # Child / Relative (primarily proves identity when calling)


@dataclass
class PairedRelationship:
    """
    Represents an established, cryptographically verified link between two family devices.
    """
    pair_id: str
    owner_phone: str      # This device's E.164 phone number
    peer_phone: str       # Paired family member's E.164 phone number
    peer_name: str        # Friendly name (e.g. "Rahul (Son)")
    role: DeviceRole      # Role of this device relative to the relationship
    k_pair: bytes         # 20-byte master shared secret (never leaves device)
    k_outbound: bytes     # Key to show code when THIS device is calling PEER
    k_inbound: bytes      # Key to verify code when PEER is calling THIS device
    k_duress: bytes       # Silent duress key for emergency alarm
    created_at: int
    step_seconds: int = DEFAULT_CODE_STEP
    revoked: bool = False

    def get_outbound_code(self, timestamp: Optional[int] = None) -> Tuple[str, int]:
        """
        Generates the 6-digit code this user reads aloud when calling the paired peer.
        Returns: (6-digit code string, remaining_seconds_in_window)
        """
        if self.revoked:
            raise ValueError("Cannot generate code for revoked relationship")

        t = int(time.time()) if timestamp is None else int(timestamp)
        code = totp(self.k_outbound, timestamp=t, step=self.step_seconds, digits=6)
        remaining = self.step_seconds - (t % self.step_seconds)
        return code, remaining

    def get_expected_inbound_code(self, timestamp: Optional[int] = None) -> Tuple[str, int]:
        """
        Returns the code this device EXPECTS the peer to read aloud right now.
        Shows the same synchronized 6 digits as the peer's outbound screen.
        Returns: (6-digit code string, remaining_seconds_in_window)
        """
        if self.revoked:
            raise ValueError("Cannot calculate expected code for revoked relationship")

        t = int(time.time()) if timestamp is None else int(timestamp)
        code = totp(self.k_inbound, timestamp=t, step=self.step_seconds, digits=6)
        remaining = self.step_seconds - (t % self.step_seconds)
        return code, remaining

    def create_lockout_session(self, max_attempts: int = 3) -> LockoutSession:
        """Creates a stateful challenge verification session with 3-strike lockout."""
        return LockoutSession(key_dir=self.k_inbound, max_attempts=max_attempts)

    def verify_incoming_code(
        self,
        candidate_code: str,
        timestamp: Optional[int] = None,
        session: Optional[LockoutSession] = None,
    ) -> VerificationResult:
        """
        Verifies the code read aloud by the peer.
        Checks [-1, 0, +1] time step window and duress triggers.
        """
        if self.revoked:
            return VerificationResult.INVALID

        t = int(time.time()) if timestamp is None else int(timestamp)
        if session is not None:
            return session.check_numeric(
                candidate=candidate_code,
                timestamp=t,
                step=self.step_seconds,
                window=1,
            )

        # One-off verification without session
        if verify_numeric(self.k_duress, candidate_code, timestamp=t, step=self.step_seconds, window=1):
            return VerificationResult.DURESS
        if verify_numeric(self.k_inbound, candidate_code, timestamp=t, step=self.step_seconds, window=1):
            return VerificationResult.SUCCESS
        return VerificationResult.INVALID


class PairingSession:
    """
    Orchestrates the creation and acceptance of pairing invitations between family devices.
    """

    @staticmethod
    def create_invitation(
        creator_phone: str,
        creator_role: DeviceRole,
        target_phone: str,
        target_name: str,
        step_seconds: int = DEFAULT_CODE_STEP,
    ) -> Tuple[str, bytes]:
        """
        Generates a pairing invitation for a targeted family phone number.
        Returns: (invitation_payload_string, k_pair_bytes)
        Zero-knowledge: K_pair is generated locally via CSPRNG.
        """
        norm_creator = normalize_phone_number(creator_phone)
        norm_target = normalize_phone_number(target_phone)

        # 160-bit CSPRNG master secret
        k_pair = os.urandom(20)
        b64_secret = base64.urlsafe_b64encode(k_pair).decode("ascii")

        # Compact URI format suitable for SMS / WhatsApp / deep-link
        params = {
            "from": norm_creator,
            "role": creator_role.value,
            "to": norm_target,
            "name": target_name,
            "sec": b64_secret,
            "step": str(step_seconds),
            "ts": str(int(time.time())),
        }
        invitation_uri = f"fvs://pair?{urllib.parse.urlencode(params)}"
        return invitation_uri, k_pair

    @staticmethod
    def accept_invitation(
        invitation_uri: str,
        acceptor_phone: str,
        acceptor_name: str,
    ) -> Tuple[PairedRelationship, PairedRelationship]:
        """
        Parses an invitation URI and establishes the reciprocal PairedRelationship
        objects for both the initiator and the acceptor.
        Validates target phone match to prevent misdirected pairing.
        """
        parsed = urllib.parse.urlparse(invitation_uri)
        if parsed.scheme != "fvs" or parsed.netloc != "pair":
            raise ValueError(f"Invalid pairing URI scheme: '{invitation_uri}'")

        params = dict(urllib.parse.parse_qsl(parsed.query))
        required = ["from", "role", "to", "sec"]
        for req in required:
            if req not in params:
                raise ValueError(f"Missing required parameter in pairing URI: {req}")

        creator_phone = normalize_phone_number(params["from"])
        target_phone = normalize_phone_number(params["to"])
        norm_acceptor = normalize_phone_number(acceptor_phone)

        # Ensure the accepting device is indeed the targeted number
        if norm_acceptor != target_phone:
            raise ValueError(
                f"Invitation target phone mismatch: expected '{target_phone}', got '{norm_acceptor}'"
            )

        k_pair = base64.urlsafe_b64decode(params["sec"].encode("ascii"))
        if len(k_pair) != 20:
            raise ValueError(f"Invalid pairing secret length: expected 20 bytes, got {len(k_pair)}")

        creator_role = DeviceRole(params["role"])
        acceptor_role = (
            DeviceRole.MEMBER if creator_role == DeviceRole.GUARDIAN else DeviceRole.GUARDIAN
        )
        step = int(params.get("step", DEFAULT_CODE_STEP))
        created_at = int(params.get("ts", int(time.time())))

        # Derive directional keys using HKDF-SHA256
        # K_A_to_B: Creator -> Acceptor
        # K_B_to_A: Acceptor -> Creator
        k_creator_to_acceptor, k_acceptor_to_creator = derive_directional_keys(k_pair)
        k_duress_acceptor = derive_duress_key(k_acceptor_to_creator)
        k_duress_creator = derive_duress_key(k_creator_to_acceptor)

        pair_id = f"pair_{creator_phone}_{target_phone}"

        # Creator's relationship representation
        creator_rel = PairedRelationship(
            pair_id=pair_id,
            owner_phone=creator_phone,
            peer_phone=target_phone,
            peer_name=params.get("name", acceptor_name),
            role=creator_role,
            k_pair=k_pair,
            k_outbound=k_creator_to_acceptor,
            k_inbound=k_acceptor_to_creator,
            k_duress=k_duress_acceptor,
            created_at=created_at,
            step_seconds=step,
        )

        # Acceptor's reciprocal relationship representation
        acceptor_rel = PairedRelationship(
            pair_id=pair_id,
            owner_phone=target_phone,
            peer_phone=creator_phone,
            peer_name=acceptor_name,
            role=acceptor_role,
            k_pair=k_pair,
            k_outbound=k_acceptor_to_creator,
            k_inbound=k_creator_to_acceptor,
            k_duress=k_duress_creator,
            created_at=created_at,
            step_seconds=step,
        )

        return creator_rel, acceptor_rel
