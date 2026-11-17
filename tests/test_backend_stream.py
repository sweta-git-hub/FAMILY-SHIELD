"""Integration and unit tests for FastAPI backend, session issuance, and WebSocket streaming."""

import json
import unittest
from unittest.mock import AsyncMock, MagicMock

try:
    from fastapi.testclient import TestClient  # type: ignore
    from server.main import create_app
    _HAS_FASTAPI_TEST = True
except ImportError:
    _HAS_FASTAPI_TEST = False

from server.config import ServerConfig
from server.session import SessionManager


class TestBackendStreamEndpoints(unittest.TestCase):
    """Tests for REST and WebSocket endpoints in server/main.py and server/stream.py."""

    def setUp(self) -> None:
        self.config = ServerConfig(
            sample_rate=16000,
            channels=1,
            chunk_duration_sec=3.0,
            chunk_stride_sec=1.0,
            session_ttl_sec=300,
            max_active_sessions=10,
        )

    def test_health_check_endpoint(self) -> None:
        if not _HAS_FASTAPI_TEST:
            self.skipTest("fastapi/starlette not installed in environment")

        app = create_app(self.config)
        client = TestClient(app)

        resp = client.get("/v1/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "family-voice-shield")
        self.assertEqual(data["sample_rate"], 16000)
        self.assertEqual(data["chunk_duration_sec"], 3.0)
        self.assertEqual(data["active_sessions"], 0)

    def test_session_creation_endpoint(self) -> None:
        if not _HAS_FASTAPI_TEST:
            self.skipTest("fastapi/starlette not installed in environment")

        app = create_app(self.config)
        client = TestClient(app)

        payload = {"device_role": "guardian", "lang": "hi"}
        resp = client.post("/v1/session", json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()

        self.assertIn("session_id", data)
        self.assertIn("token", data)
        self.assertIn("websocket_url", data)
        self.assertEqual(data["sample_rate"], 16000)
        self.assertEqual(data["channels"], 1)
        self.assertEqual(data["chunk_duration_sec"], 3.0)

        # Check session manager state
        mgr: SessionManager = app.state.session_manager
        self.assertEqual(mgr.active_count, 1)

    def test_websocket_unauthorized_token(self) -> None:
        if not _HAS_FASTAPI_TEST:
            self.skipTest("fastapi/starlette not installed in environment")

        app = create_app(self.config)
        client = TestClient(app)

        # Attempt WebSocket connection with invalid token
        with self.assertRaises(Exception):
            with client.websocket_connect("/v1/stream?token=invalid_bogus_token") as ws:
                pass

    def test_websocket_handshake_and_audio_flow(self) -> None:
        if not _HAS_FASTAPI_TEST:
            self.skipTest("fastapi/starlette not installed in environment")

        app = create_app(self.config)
        client = TestClient(app)

        # 1. Create valid session
        s_resp = client.post("/v1/session", json={"device_role": "guardian", "lang": "hi"})
        token = s_resp.json()["token"]
        session_id = s_resp.json()["session_id"]

        # 2. Connect WebSocket
        with client.websocket_connect(f"/v1/stream?token={token}") as ws:
            # Send start handshake
            ws.send_text(json.dumps({
                "type": "start",
                "session": session_id,
                "sr": 16000,
                "channels": 1,
            }))

            ready_msg = json.loads(ws.receive_text())
            self.assertEqual(ready_msg.get("type"), "ready")
            self.assertEqual(ready_msg.get("session"), session_id)

            # Send call context
            ws.send_text(json.dumps({
                "type": "context",
                "unknown_number": True,
                "claims_relative": True,
            }))

            # Stream 3.0 seconds of synthetic 16kHz PCM audio
            # 16000 samples * 2 bytes = 32000 bytes/sec -> 3.0s = 96000 bytes
            pcm_chunk = b"\x01\x00" * 48000
            ws.send_bytes(pcm_chunk)

            # Receive score feedback frame
            score_msg = json.loads(ws.receive_text())
            self.assertEqual(score_msg.get("type"), "score")
            self.assertIn("risk", score_msg)
            self.assertIn("tier", score_msg)
            self.assertTrue(score_msg.get("mock"))

            # Clean teardown
            ws.send_text(json.dumps({"type": "end"}))

    def test_websocket_reconnect(self) -> None:
        if not _HAS_FASTAPI_TEST:
            self.skipTest("fastapi/starlette not installed in environment")

        app = create_app(self.config)
        client = TestClient(app)

        # First session
        resp1 = client.post("/v1/session", json={})
        token1 = resp1.json()["token"]
        with client.websocket_connect(f"/v1/stream?token={token1}") as ws1:
            ws1.send_text(json.dumps({"type": "end"}))

        # Reconnect with new session
        resp2 = client.post("/v1/session", json={})
        token2 = resp2.json()["token"]
        with client.websocket_connect(f"/v1/stream?token={token2}") as ws2:
            ws2.send_text(json.dumps({
                "type": "start",
                "session": resp2.json()["session_id"],
            }))
            ready = json.loads(ws2.receive_text())
            self.assertEqual(ready.get("type"), "ready")
            ws2.send_text(json.dumps({"type": "end"}))


class TestReplayClientLogic(unittest.TestCase):
    """Unit tests for synthetic audio generation and stats in client_replay.py."""

    def test_synthetic_stream_generation(self) -> None:
        from server.client_replay import StreamStats, generate_synthetic_stream

        pcm = generate_synthetic_stream(duration_sec=1.0, sample_rate=16000, freq_hz=440.0)
        # 1.0 second * 16000 samples * 2 bytes = 32000 bytes
        self.assertEqual(len(pcm), 32000)

        stats = StreamStats()
        stats.latencies_ms = [10.5, 15.0, 20.0]
        self.assertAlmostEqual(stats.avg_latency_ms, 15.1666, places=2)
        self.assertEqual(stats.min_latency_ms, 10.5)
        self.assertEqual(stats.max_latency_ms, 20.0)


if __name__ == "__main__":
    unittest.main()
