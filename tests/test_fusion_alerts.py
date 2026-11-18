"""Unit and integration tests for Phase 7: Multimodal Fusion & Client Alerts.

Tests:
1. Calibrated logistic fusion model: logit math, sigmoid bounds, monotonicity.
2. Fail-safe critical overrides for voice clone (s_a) and scam language (s_t).
3. Modality attribution (acoustic vs semantic vs context).
4. Alert tier state machine: fast escalation vs damped hysteresis de-escalation.
5. Spoken advisory accessibility generation in English and Hindi.
6. HMAC-SHA256 signed emergency family broadcast payload.
7. StreamScorer integration with calibrated fusion and tier tracking.
"""

from __future__ import annotations

import hashlib
import hmac
import unittest
from core.alert_tiers import AlertStateMachine, AlertTier, AlertTransition, EmergencyNotification
from ml.antispoof_engine import MockAntiSpoofEngine
from ml.fusion import FusionResult, MultimodalFusionEngine
from ml.stt_engine import MockSTTEngine
from server.chunker import AudioChunk
from server.scorer import StreamScorer


class TestMultimodalFusionEngine(unittest.TestCase):
    """Tests logistic fusion formulation, sigmoid bounds, and critical overrides."""

    def setUp(self) -> None:
        self.fusion = MultimodalFusionEngine()

    def test_benign_speech_produces_low_risk(self) -> None:
        res = self.fusion.fuse(s_a=0.05, s_t=0.05, s_c=0.05)
        self.assertLess(res.fused_risk, 0.20)
        self.assertFalse(res.is_critical_override)
        self.assertEqual(res.dominant_modality, "none")

    def test_sigmoid_strictly_bounded(self) -> None:
        # Test boundary extremes
        res_min = self.fusion.fuse(s_a=0.0, s_t=0.0, s_c=0.0)
        self.assertTrue(0.0 <= res_min.fused_risk <= 1.0)

        res_max = self.fusion.fuse(s_a=1.0, s_t=1.0, s_c=1.0)
        self.assertTrue(0.0 <= res_max.fused_risk <= 1.0)
        self.assertGreaterEqual(res_max.fused_risk, 0.95)

    def test_monotonic_risk_escalation(self) -> None:
        res1 = self.fusion.fuse(s_a=0.10, s_t=0.10, s_c=0.05)
        res2 = self.fusion.fuse(s_a=0.30, s_t=0.10, s_c=0.05)
        res3 = self.fusion.fuse(s_a=0.30, s_t=0.45, s_c=0.05)
        res4 = self.fusion.fuse(s_a=0.30, s_t=0.45, s_c=0.25)

        self.assertLess(res1.fused_risk, res2.fused_risk)
        self.assertLess(res2.fused_risk, res3.fused_risk)
        self.assertLess(res3.fused_risk, res4.fused_risk)

    def test_critical_voice_clone_override(self) -> None:
        # High acoustic spoofing (s_a = 0.88), but benign chatter (s_t = 0.05)
        res = self.fusion.fuse(s_a=0.88, s_t=0.05, s_c=0.05)
        self.assertGreaterEqual(res.fused_risk, 0.70)
        self.assertTrue(res.is_critical_override)
        self.assertEqual(res.dominant_modality, "acoustic")

    def test_critical_scam_language_override(self) -> None:
        # Natural human caller (s_a = 0.08), but severe extortion threat (s_t = 0.95)
        res = self.fusion.fuse(s_a=0.08, s_t=0.95, s_c=0.10)
        self.assertGreaterEqual(res.fused_risk, 0.70)
        self.assertTrue(res.is_critical_override)
        self.assertEqual(res.dominant_modality, "semantic")


class TestAlertStateMachine(unittest.TestCase):
    """Tests alert tier transitions, hysteresis debouncing, and emergency payload signing."""

    def setUp(self) -> None:
        self.sm = AlertStateMachine(
            amber_threshold=0.40,
            red_threshold=0.70,
            amber_deescalate_threshold=0.32,
            red_deescalate_threshold=0.60,
            deescalate_patience_chunks=2,
            secret_key=b"test-secret-key-12345",
        )

    def test_initial_state_is_green(self) -> None:
        self.assertEqual(self.sm.current_tier, AlertTier.GREEN)
        self.assertEqual(self.sm.get_prompt_action(), "normal")

    def test_fast_escalation_to_amber_and_red(self) -> None:
        # Instant escalation to AMBER on 1st chunk
        tier, trans1 = self.sm.update(0.48, reasons=["suspicious_phrases"], timestamp=3.0)
        self.assertEqual(tier, AlertTier.AMBER)
        self.assertIsNotNone(trans1)
        self.assertTrue(trans1.is_escalation)
        self.assertEqual(self.sm.get_prompt_action(), "ask_for_code")

        # Instant escalation to RED on 1st chunk
        tier, trans2 = self.sm.update(0.85, reasons=["voice_clone_detected"], timestamp=6.0)
        self.assertEqual(tier, AlertTier.RED)
        self.assertIsNotNone(trans2)
        self.assertTrue(trans2.is_escalation)

    def test_hysteresis_debouncing_prevents_premature_deescalation(self) -> None:
        # Escalate to RED
        self.sm.update(0.80, timestamp=3.0)
        self.assertEqual(self.sm.current_tier, AlertTier.RED)

        # Risk drops to 0.50 (below red_deescalate 0.60) on chunk 1:
        # Should stay RED because patience is 2 chunks!
        tier, trans = self.sm.update(0.50, timestamp=6.0)
        self.assertEqual(tier, AlertTier.RED)
        self.assertIsNone(trans)

        # 2nd consecutive chunk below 0.60: now de-escalates to AMBER
        tier, trans = self.sm.update(0.50, timestamp=9.0)
        self.assertEqual(tier, AlertTier.AMBER)
        self.assertIsNotNone(trans)
        self.assertFalse(trans.is_escalation)

    def test_spoken_advisory_bilingual(self) -> None:
        self.sm.current_tier = AlertTier.GREEN
        self.assertIn("सामान्य", self.sm.get_spoken_advisory("hi"))
        self.assertIn("normal", self.sm.get_spoken_advisory("en").lower())

        self.sm.current_tier = AlertTier.AMBER
        self.assertIn("सतर्क", self.sm.get_spoken_advisory("hi"))
        self.assertIn("caution", self.sm.get_spoken_advisory("en").lower())

        self.sm.current_tier = AlertTier.RED
        self.assertIn("चेतावनी", self.sm.get_spoken_advisory("hi"))
        self.assertIn("warning", self.sm.get_spoken_advisory("en").lower())

    def test_emergency_notification_signing(self) -> None:
        self.sm.current_tier = AlertTier.RED
        notif = self.sm.generate_emergency_notification(
            target_phone="+919876543210",
            fused_risk=0.88,
            dominant_modality="acoustic",
            reasons=["voice_clone", "unknown_number"],
        )
        self.assertEqual(notif.tier, "RED")
        self.assertIn("***", notif.masked_target_phone)
        self.assertTrue(len(notif.signature) == 64)  # Hex-encoded SHA-256 HMAC

        # Verify signature validity
        sig_data = f"{notif.notification_id}:{notif.timestamp}:RED:{round(notif.risk_score, 4)}:{notif.masked_target_phone}".encode()
        expected_sig = hmac.new(b"test-secret-key-12345", sig_data, hashlib.sha256).hexdigest()
        self.assertEqual(notif.signature, expected_sig)


class TestStreamScorerIntegrationWithFusion(unittest.TestCase):
    """Tests end-to-end StreamScorer with MultimodalFusionEngine and AlertStateMachine."""

    def test_stream_scorer_multimodal_flow(self) -> None:
        mock_stt = MockSTTEngine(default_text="Hello dad, need money right now jaldi")
        mock_as = MockAntiSpoofEngine(default_score=0.82)
        scorer = StreamScorer(stt_engine=mock_stt, antispoof_engine=mock_as)

        chunk = AudioChunk(
            chunk_index=1,
            timestamp_sec=3.0,
            data=b"\x12\x00" * 24000,
            duration_sec=3.0,
            sample_rate=16000,
            channels=1,
            rms_energy=0.04,
            has_speech=True,
        )
        score = scorer.score_chunk(chunk, call_context={"unknown_number": True})

        self.assertEqual(score.tier, "RED")
        self.assertGreaterEqual(score.risk, 0.70)
        self.assertEqual(score.prompt, "ask_for_code")
        self.assertIn(score.dominant_modality, ("acoustic", "semantic"))
        self.assertIn("dominant_modality", score.to_dict())


if __name__ == "__main__":
    unittest.main()
