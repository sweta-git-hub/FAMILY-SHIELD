"""Unit tests for ephemeral SessionManager."""

import time
import unittest
from server.session import SessionManager


class TestSessionManager(unittest.TestCase):

    def setUp(self) -> None:
        self.mgr = SessionManager(max_active_sessions=5, default_ttl_sec=3600)

    def test_create_session_success(self) -> None:
        rec = self.mgr.create_session(device_role="guardian", lang="hi")
        self.assertIsNotNone(rec.session_id)
        self.assertIsNotNone(rec.token)
        self.assertEqual(rec.device_role, "guardian")
        self.assertEqual(rec.lang, "hi")
        self.assertFalse(rec.is_active)
        self.assertEqual(self.mgr.active_count, 1)

    def test_validate_token_success_and_failure(self) -> None:
        rec = self.mgr.create_session(device_role="member")
        valid = self.mgr.validate_token(rec.token)
        self.assertIsNotNone(valid)
        self.assertEqual(valid.session_id, rec.session_id)

        # Invalid token
        invalid = self.mgr.validate_token("non_existent_token_123")
        self.assertIsNone(invalid)

    def test_session_activation(self) -> None:
        rec = self.mgr.create_session()
        self.assertFalse(rec.is_active)
        activated = self.mgr.activate_session(rec.token)
        self.assertIsNotNone(activated)
        self.assertTrue(activated.is_active)

    def test_session_expiration(self) -> None:
        # Create session with 0-second TTL
        rec = self.mgr.create_session(ttl_sec=0)
        time.sleep(0.01)
        self.assertTrue(rec.is_expired)
        self.assertIsNone(self.mgr.validate_token(rec.token))
        self.assertEqual(self.mgr.active_count, 0)

    def test_close_session_by_id_and_token(self) -> None:
        rec1 = self.mgr.create_session()
        rec2 = self.mgr.create_session()
        self.assertEqual(self.mgr.active_count, 2)

        # Close rec1 by session_id
        self.mgr.close_session(rec1.session_id)
        self.assertEqual(self.mgr.active_count, 1)
        self.assertIsNone(self.mgr.validate_token(rec1.token))

        # Close rec2 by token
        self.mgr.close_session(rec2.token)
        self.assertEqual(self.mgr.active_count, 0)

    def test_max_capacity_limit(self) -> None:
        for _ in range(5):
            self.mgr.create_session()
        self.assertEqual(self.mgr.active_count, 5)

        with self.assertRaises(ValueError):
            self.mgr.create_session()


if __name__ == "__main__":
    unittest.main()
