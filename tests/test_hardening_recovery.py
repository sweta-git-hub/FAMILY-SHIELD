"""Hardening, Concurrency, and Failure Recovery Test Suite for Family Voice Shield.

Evaluates system resilience against:
1. Concurrency throttling and session capacity saturation.
2. Malformed packet injection (odd-byte lengths, clipped signals, corrupt payloads).
3. Audio chunker buffer overflow and backpressure memory caps.
4. Sudden WebSocket disconnect recovery and orphaned session cleanup.
"""

from __future__ import annotations

import json
import unittest

try:
    from fastapi.testclient import TestClient
    from server.main import create_app
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False

from server.chunker import AudioChunker
from server.config import ServerConfig
from server.session import SessionManager


class TestConcurrencyAndSessionLimits(unittest.TestCase):
    """Tests server behavior under concurrent load and capacity boundaries."""

    def test_session_capacity_throttling_and_recovery(self) -> None:
        """Verify strict session capacity throttling and subsequent capacity reclamation."""
        max_sessions = 5
        mgr = SessionManager(max_active_sessions=max_sessions, default_ttl_sec=3600)

        created_sessions = []
        for i in range(max_sessions):
            rec = mgr.create_session(device_role="guardian", lang="hi")
            created_sessions.append(rec)

        self.assertEqual(mgr.active_count, max_sessions)

        # 6th session must be rejected with capacity error
        with self.assertRaises(ValueError):
            mgr.create_session(device_role="guardian", lang="hi")

        # Closing one session immediately frees capacity
        mgr.close_session(created_sessions[0].session_id)
        self.assertEqual(mgr.active_count, max_sessions - 1)

        # Now 6th session succeeds
        new_rec = mgr.create_session(device_role="guardian", lang="hi")
        self.assertIsNotNone(new_rec)
        self.assertEqual(mgr.active_count, max_sessions)


class TestMalformedPacketHardening(unittest.TestCase):
    """Tests chunker and pipeline stability against corrupt or truncated audio frames."""

    def test_odd_byte_length_does_not_crash_chunker(self) -> None:
        """Client streams odd number of bytes (broken 16-bit integer boundary)."""
        chunker = AudioChunker(sample_rate=16000, chunk_duration_sec=3.0, chunk_stride_sec=1.0)
        # Push 3199 bytes (odd byte length)
        odd_bytes = b"\x01" * 3199
        chunks = chunker.push_pcm(odd_bytes)
        self.assertIsInstance(chunks, list)

        # Chunker must retain alignment and handle subsequent even frame
        even_bytes = b"\x02" * 3201  # Brings total to 6400 bytes (even)
        chunks2 = chunker.push_pcm(even_bytes)
        self.assertIsInstance(chunks2, list)

    def test_extreme_clipping_and_dc_offset_no_crash(self) -> None:
        """Audio with maximum clipping (+32767 / -32768) and flat DC offset."""
        import struct
        chunker = AudioChunker(sample_rate=16000, chunk_duration_sec=3.0, chunk_stride_sec=1.0)
        # Fully saturated square wave
        clipped_pcm = (struct.pack("<h", 32767) * 800) + (struct.pack("<h", -32768) * 800)
        # 60 frames = 6 seconds
        emitted = []
        for _ in range(60):
            emitted.extend(chunker.push_pcm(clipped_pcm))

        self.assertGreater(len(emitted), 0)
        for ch in emitted:
            self.assertTrue(ch.has_speech)
            self.assertGreater(ch.rms_energy, 0.5)

    def test_buffer_overflow_backpressure_eviction(self) -> None:
        """Push 20 seconds of audio into chunker (exceeds 12.0s max capacity).

        Asserts that oldest bytes are discarded cleanly and buffer capacity does not grow unbounded.
        """
        chunker = AudioChunker(
            sample_rate=16000,
            chunk_duration_sec=3.0,
            chunk_stride_sec=1.0,
            max_buffer_sec=12.0,
        )
        # 20 seconds of audio = 640,000 bytes
        huge_audio = b"\x05\x00" * (16000 * 20)
        chunks = chunker.push_pcm(huge_audio)

        # Chunks must be emitted
        self.assertGreater(len(chunks), 0)
        # Internal buffer size must be strictly bounded below max_buffer_bytes
        self.assertLessEqual(len(chunker._buffer), chunker.max_buffer_bytes)


class TestWebSocketDisconnectRecovery(unittest.TestCase):
    """Integration test for abrupt disconnect recovery and session reclamation."""

    def test_abrupt_disconnect_cleans_up_session(self) -> None:
        """Client disconnects abruptly mid-stream without sending 'end' frame."""
        if not _HAS_FASTAPI:
            self.skipTest("FastAPI not installed in environment")

        cfg = ServerConfig(max_active_sessions=5, session_ttl_sec=300)
        app = create_app(cfg)
        client = TestClient(app)

        # Create session
        s_resp = client.post("/v1/session", json={"device_role": "guardian"})
        token = s_resp.json()["token"]
        session_id = s_resp.json()["session_id"]

        mgr: SessionManager = app.state.session_manager
        self.assertEqual(mgr.active_count, 1)

        # Connect and stream 1 frame, then drop connection immediately without 'end'
        with client.websocket_connect(f"/v1/stream?token={token}") as ws:
            ws.send_text(json.dumps({"type": "start", "session": session_id}))
            ready = json.loads(ws.receive_text())
            self.assertEqual(ready["type"], "ready")
            ws.send_bytes(b"\x01\x00" * 1600)

        # After exiting context manager (connection closed), session must be closed cleanly
        self.assertEqual(mgr.active_count, 0)
        self.assertIsNone(mgr.validate_token(token))


if __name__ == "__main__":
    unittest.main()
