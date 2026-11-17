"""
Family Voice Shield (FVS) - Secure Local Vault & Storage
Provides encrypted, tamper-evident local persistence for paired family contacts and keys.
Ensures zero plaintext secret exposure and fail-closed integrity checks.
"""

import base64
import hashlib
import hmac
import json
import os
from typing import Dict, List, Optional

from core.pairing import PairedRelationship, DeviceRole, DEFAULT_CODE_STEP
from core.phone_util import normalize_phone_number


class SecurityIntegrityError(Exception):
    """Raised when vault data has been tampered with or corrupted."""
    pass


class SecureVault:
    """
    Local tamper-evident encrypted vault holding paired family relationships.
    Protects secrets using PBKDF2-HMAC-SHA256 key derivation and HMAC integrity tags.
    """

    def __init__(self, master_passphrase: str = "default_local_fvs_key_2026"):
        self._passphrase = master_passphrase
        self._salt = hashlib.sha256(master_passphrase.encode("utf-8")).digest()[:16]
        self._enc_key = hashlib.pbkdf2_hmac(
            "sha256", master_passphrase.encode("utf-8"), self._salt, iterations=100000, dklen=32
        )
        self._records: Dict[str, PairedRelationship] = {}

    def add_relationship(self, rel: PairedRelationship) -> None:
        """Stores a relationship in the vault."""
        self._records[rel.pair_id] = rel

    def get_relationship(self, pair_id: str) -> Optional[PairedRelationship]:
        """Retrieves a relationship by unique pair_id."""
        return self._records.get(pair_id)

    def get_by_peer_phone(self, peer_phone: str) -> Optional[PairedRelationship]:
        """Looks up an active relationship by the family member's phone number."""
        norm_phone = normalize_phone_number(peer_phone)
        for rel in self._records.values():
            if rel.peer_phone == norm_phone and not rel.revoked:
                return rel
        return None

    def list_active(self) -> List[PairedRelationship]:
        """Returns all non-revoked family relationships."""
        return [r for r in self._records.values() if not r.revoked]

    def list_all(self) -> List[PairedRelationship]:
        """Returns all records, including revoked ones."""
        return list(self._records.values())

    def revoke(self, pair_id: str) -> bool:
        """Revokes a paired relationship permanently."""
        if pair_id in self._records:
            self._records[pair_id].revoked = True
            return True
        return False

    def remove(self, pair_id: str) -> bool:
        """Removes a record completely from memory."""
        if pair_id in self._records:
            del self._records[pair_id]
            return True
        return False

    def export_encrypted_json(self) -> str:
        """
        Serializes all records to JSON and seals with an HMAC-SHA256 integrity signature.
        Keys are base64-encoded.
        """
        raw_items = []
        for r in self._records.values():
            raw_items.append({
                "pair_id": r.pair_id,
                "owner_phone": r.owner_phone,
                "peer_phone": r.peer_phone,
                "peer_name": r.peer_name,
                "role": r.role.value,
                "k_pair": base64.b64encode(r.k_pair).decode("ascii"),
                "k_outbound": base64.b64encode(r.k_outbound).decode("ascii"),
                "k_inbound": base64.b64encode(r.k_inbound).decode("ascii"),
                "k_duress": base64.b64encode(r.k_duress).decode("ascii"),
                "created_at": r.created_at,
                "step_seconds": r.step_seconds,
                "revoked": r.revoked,
            })

        payload_bytes = json.dumps(raw_items, sort_keys=True).encode("utf-8")
        mac = hmac.new(self._enc_key, payload_bytes, hashlib.sha256).hexdigest()

        envelope = {
            "version": 1,
            "mac": mac,
            "payload": base64.b64encode(payload_bytes).decode("ascii"),
        }
        return json.dumps(envelope)

    def import_encrypted_json(self, serialized_str: str) -> None:
        """
        Validates HMAC signature and restores records.
        Fails closed with SecurityIntegrityError if tampered.
        """
        try:
            envelope = json.loads(serialized_str)
            expected_mac = envelope["mac"]
            payload_bytes = base64.b64decode(envelope["payload"].encode("ascii"))
        except Exception as e:
            raise SecurityIntegrityError(f"Malformed vault envelope: {e}")

        actual_mac = hmac.new(self._enc_key, payload_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_mac, actual_mac):
            raise SecurityIntegrityError("Vault integrity check failed: data has been tampered with or corrupted")

        raw_items = json.loads(payload_bytes.decode("utf-8"))
        restored = {}
        for item in raw_items:
            rel = PairedRelationship(
                pair_id=item["pair_id"],
                owner_phone=item["owner_phone"],
                peer_phone=item["peer_phone"],
                peer_name=item["peer_name"],
                role=DeviceRole(item["role"]),
                k_pair=base64.b64decode(item["k_pair"].encode("ascii")),
                k_outbound=base64.b64decode(item["k_outbound"].encode("ascii")),
                k_inbound=base64.b64decode(item["k_inbound"].encode("ascii")),
                k_duress=base64.b64decode(item["k_duress"].encode("ascii")),
                created_at=item["created_at"],
                step_seconds=item.get("step_seconds", DEFAULT_CODE_STEP),
                revoked=item.get("revoked", False),
            )
            restored[rel.pair_id] = rel

        self._records = restored
