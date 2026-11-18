"""Automated Privacy and Security Audit Test Suite for Family Voice Shield.

Enforces Rule 7 and core security guarantees:
1. Zero raw audio or transcripts persisted to disk during high-volume streaming.
2. Immediate in-memory buffer release upon session teardown.
3. Strict log sanitization stripping sensitive keys (audio, pcm, transcripts, secrets, phone numbers).
4. Vault cryptographic integrity and tamper detection (fail-closed security).
"""

from __future__ import annotations

import io
import json
import logging
import os
import tempfile
import unittest

from core.pairing import DeviceRole, PairedRelationship
from core.storage import SecureVault, SecurityIntegrityError
from server.chunker import AudioChunker
from server.logger import StructuredJsonFormatter, get_logger, log_event
from server.scorer import StreamScorer
from server.session import SessionManager


class TestZeroDiskPersistenceAudit(unittest.TestCase):
    """Audits filesystem to guarantee zero audio or transcript persistence (Rule 7)."""

    def test_high_volume_streaming_writes_zero_disk_files(self) -> None:
        """Stream 50 consecutive PCM chunks and assert zero temporary files created."""
        temp_dir = tempfile.gettempdir()
        initial_temp_files = set(os.listdir(temp_dir))

        chunker = AudioChunker(sample_rate=16000, chunk_duration_sec=3.0, chunk_stride_sec=1.0)
        scorer = StreamScorer()

        # 50 frames of 100ms PCM audio (5.0 seconds continuous stream)
        frame_100ms = b"\x05\x00" * 1600  # 3200 bytes per frame
        emitted_chunks = []

        for _ in range(50):
            chunks = chunker.push_pcm(frame_100ms)
            for ch in chunks:
                emitted_chunks.append(ch)
                score = scorer.score_chunk(ch)
                self.assertIsNotNone(score)

        self.assertGreater(len(emitted_chunks), 0)

        # Check that no new files matching audio or transcript extensions were created
        current_temp_files = set(os.listdir(temp_dir))
        new_files = current_temp_files - initial_temp_files
        suspicious_extensions = (".wav", ".pcm", ".raw", ".mp3", ".txt", ".transcript")

        for f in new_files:
            self.assertFalse(
                f.lower().endswith(suspicious_extensions),
                f"Rule 7 Violation! Found disk file generated during streaming: {f}",
            )

        # Clean reset
        chunker.reset()
        self.assertEqual(chunker.chunks_emitted, 0)
        self.assertEqual(chunker.total_bytes_received, 0)


class TestMemoryLifecycleAudit(unittest.TestCase):
    """Verifies immediate in-memory cleanup on session closure."""

    def test_session_closure_releases_memory_record(self) -> None:
        """Session termination immediately purges session token from RAM."""
        mgr = SessionManager(max_active_sessions=10, default_ttl_sec=3600)
        rec = mgr.create_session(device_role="guardian", lang="hi")

        self.assertEqual(mgr.active_count, 1)
        self.assertIsNotNone(mgr.validate_token(rec.token))

        # Close session
        mgr.close_session(rec.session_id)
        self.assertEqual(mgr.active_count, 0)
        self.assertIsNone(mgr.validate_token(rec.token))


class TestLogSanitizationAudit(unittest.TestCase):
    """Verifies that structured JSON logger scrubs all sensitive keys."""

    def test_forbidden_sensitive_keys_are_redacted_from_logs(self) -> None:
        """Feed forbidden sensitive fields to logger and assert none leak into JSON output."""
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(StructuredJsonFormatter())

        test_logger = logging.getLogger("fvs_audit_test")
        test_logger.setLevel(logging.INFO)
        test_logger.addHandler(handler)
        test_logger.propagate = False

        # Attempt to log sensitive credentials and audio metadata
        log_event(
            test_logger,
            logging.INFO,
            "test_audit_event",
            "Streaming chunk processed",
            session_id="session-12345",
            # Forbidden sensitive fields that MUST be stripped:
            audio=b"\x00\x01\x02\x03",
            raw_audio="binary_audio_data",
            pcm="pcm_raw_samples",
            bytes="bytes_payload",
            transcript="Hello, transfer fifty thousand rupees immediately",
            text="CBI digital arrest warrant",
            secret="super_secret_master_key",
            key="aes_vault_key",
            totp="123456",
            code="654321",
            phone="+919876543210",
            phone_number="+919876543210",
            e164="+919876543210",
            # Allowed safe metadata:
            chunk_index=5,
            duration_sec=3.0,
            risk_score=0.85,
        )

        handler.flush()
        log_line = log_stream.getvalue().strip()
        self.assertTrue(log_line)

        log_data = json.loads(log_line)
        self.assertEqual(log_data["event_type"], "test_audit_event")
        self.assertEqual(log_data["session_id"], "session-12345")
        self.assertEqual(log_data["chunk_index"], 5)
        self.assertEqual(log_data["risk_score"], 0.85)

        # Assert every single forbidden key is missing from JSON
        forbidden_keys = [
            "audio", "raw_audio", "pcm", "bytes", "transcript", "text",
            "secret", "key", "totp", "code", "phone", "phone_number", "e164",
        ]
        for key in forbidden_keys:
            self.assertNotIn(
                key,
                log_data,
                f"Privacy Leak! Forbidden sensitive key '{key}' appeared in structured log!",
            )


class TestVaultTamperDefenseAudit(unittest.TestCase):
    """Verifies fail-closed behavior of SecureVault under tampering."""

    def test_vault_tamper_detection_fails_closed(self) -> None:
        """Tampering with encrypted vault payload triggers fail-closed error."""
        vault = SecureVault(master_passphrase="StrongMasterPassword123!")
        rel = PairedRelationship(
            pair_id="pair_rahul",
            owner_phone="+919876543210",
            peer_phone="+919876543211",
            peer_name="Rahul",
            role=DeviceRole.GUARDIAN,
            k_pair=b"01234567890123456789",
            k_outbound=b"abcdefghijklmnopqrst",
            k_inbound=b"12345678901234567890",
            k_duress=b"duresskey12345678901",
            created_at=1700000000,
            step_seconds=60,
        )
        vault.add_relationship(rel)

        exported_json = vault.export_encrypted_json()
        exported_data = json.loads(exported_json)
        self.assertIn("payload", exported_data)
        self.assertIn("mac", exported_data)

        # Corrupt the HMAC tag
        corrupted_data = dict(exported_data)
        corrupted_data["mac"] = "0000000000000000000000000000000000000000000000000000000000000000"
        corrupted_json = json.dumps(corrupted_data)

        # Importing corrupted vault must fail closed with SecurityIntegrityError
        new_vault = SecureVault(master_passphrase="StrongMasterPassword123!")
        with self.assertRaises(SecurityIntegrityError):
            new_vault.import_encrypted_json(corrupted_json)


if __name__ == "__main__":
    unittest.main()
