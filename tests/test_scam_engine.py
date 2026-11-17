"""Unit and integration tests for Phase 5: Scam Engine.

Tests:
1. Lexicon pattern matching across Hindi (Devanagari), Hinglish, and English.
2. Scam category coverage (authority, secrecy, financial, distress, urgency, device excuse).
3. Noisy-OR classifier math: monotonicity, prior limits, multi-cue combination.
4. STT engine wrapper with simulated cues and in-memory transcription.
5. StreamScorer integration with real semantic scoring and WebSocket payload formatting.
"""

from __future__ import annotations

import unittest
from ml.scam_lexicon import ScamCategory, ScamLexicon, CATEGORY_PRIORS
from ml.scam_classifier import NoisyOrScamClassifier
from ml.stt_engine import MockSTTEngine, create_stt_engine
from server.chunker import AudioChunk
from server.scorer import StreamScorer, RiskScore


class TestScamLexicon(unittest.TestCase):
    """Tests multilingual lexicon matching and category assignment."""

    def setUp(self) -> None:
        self.lexicon = ScamLexicon()

    def test_english_authority_patterns(self) -> None:
        text = "This is CBI officer speaking, there is a police case and arrest warrant against you"
        cats = self.lexicon.extract_categories(text)
        self.assertIn(ScamCategory.AUTHORITY, cats)
        self.assertTrue(any("cbi" in match.lower() or "police" in match.lower() for match in cats[ScamCategory.AUTHORITY]))

    def test_devanagari_patterns(self) -> None:
        # Digital arrest + UPI transfer
        text = "डिजिटल अरेस्ट किया गया है, तुरंत यूपीआई से पैसे भेजो"
        cats = self.lexicon.extract_categories(text)
        self.assertIn(ScamCategory.AUTHORITY, cats)
        self.assertIn(ScamCategory.FINANCIAL, cats)
        self.assertIn(ScamCategory.URGENCY, cats)

    def test_hinglish_patterns(self) -> None:
        text = "Papa mera accident ho gaya hai hospital mein hu, kisi ko mat batana, turant paise transfer karo"
        cats = self.lexicon.extract_categories(text)
        self.assertIn(ScamCategory.DISTRESS, cats)
        self.assertIn(ScamCategory.SECRECY, cats)
        self.assertIn(ScamCategory.URGENCY, cats)
        self.assertIn(ScamCategory.FINANCIAL, cats)

    def test_device_excuse_pattern(self) -> None:
        text = "Mera phone damage ho gaya hai, friend's phone se call kar raha hu, naya number hai"
        cats = self.lexicon.extract_categories(text)
        self.assertIn(ScamCategory.DEVICE_EXCUSE, cats)

    def test_benign_conversations(self) -> None:
        text = "Hi Grandma, how are you? What did you make for dinner today? I will visit this weekend."
        cats = self.lexicon.extract_categories(text)
        self.assertEqual(len(cats), 0)


class TestNoisyOrScamClassifier(unittest.TestCase):
    """Tests probabilistic Noisy-OR classification properties."""

    def setUp(self) -> None:
        self.classifier = NoisyOrScamClassifier(background_leak=0.05)

    def test_empty_or_benign_text_returns_baseline(self) -> None:
        res = self.classifier.classify_text("Hello beta, everything is fine at home")
        self.assertAlmostEqual(res.s_t, 0.05, places=2)
        self.assertFalse(res.is_suspicious)
        self.assertFalse(res.is_critical)

    def test_single_high_risk_category(self) -> None:
        # Authority alone has prior 0.85
        # P = 1 - (1 - 0.05) * (1 - 0.85) = 1 - 0.95 * 0.15 = 1 - 0.1425 = 0.8575
        res = self.classifier.classify_text("This is Crime Branch and CBI, you are under digital arrest")
        self.assertIn(ScamCategory.AUTHORITY, res.matched_categories)
        self.assertGreaterEqual(res.s_t, 0.80)
        self.assertTrue(res.is_critical)
        self.assertEqual(res.highest_risk_category, ScamCategory.AUTHORITY.value)

    def test_compound_escalation_monotonicity(self) -> None:
        # Mild urgency alone
        res1 = self.classifier.classify_text("Please do it quickly right now")
        # Urgency + Secrecy
        res2 = self.classifier.classify_text("Right now jaldi, and don't tell anyone stay on the line")
        # Urgency + Secrecy + Payment
        res3 = self.classifier.classify_text("Right now jaldi, don't tell anyone, scan the QR code and send UPI money")

        self.assertLess(res1.s_t, res2.s_t)
        self.assertLess(res2.s_t, res3.s_t)
        self.assertTrue(res3.is_critical)

    def test_score_phrases_convenience(self) -> None:
        score = self.classifier.score_phrases(["police case", "transfer money immediately"])
        self.assertGreater(score, 0.70)


class TestSTTEngineAndScorer(unittest.TestCase):
    """Tests STT engine wrapper and integration with StreamScorer."""

    def test_mock_stt_transcription(self) -> None:
        mock_stt = MockSTTEngine(default_text="benign family chatter")
        pcm = b"\x00\x00" * 16000  # 1 second of silence
        res = mock_stt.transcribe_pcm(pcm, sample_rate=16000)
        self.assertEqual(res.text, "benign family chatter")
        self.assertTrue(res.is_mock)
        self.assertAlmostEqual(res.duration_sec, 1.0)

    def test_stream_scorer_benign_audio(self) -> None:
        mock_stt = MockSTTEngine(default_text="Hello dad, having lunch today with colleagues")
        scorer = StreamScorer(stt_engine=mock_stt)
        
        chunk = AudioChunk(
            chunk_index=1,
            timestamp_sec=3.0,
            data=b"\x05\x00" * 24000,
            duration_sec=3.0,
            sample_rate=16000,
            channels=1,
            rms_energy=0.03,
            has_speech=True,
        )
        score = scorer.score_chunk(chunk, call_context={"unknown_number": False})
        
        self.assertEqual(score.tier, "GREEN")
        self.assertLess(score.risk, 0.40)
        self.assertEqual(score.prompt, "normal")

    def test_stream_scorer_critical_scam_audio(self) -> None:
        mock_stt = MockSTTEngine(
            default_text="Police arrest warrant hai, don't tell anyone, send UPI transfer immediately"
        )
        scorer = StreamScorer(stt_engine=mock_stt)
        
        chunk = AudioChunk(
            chunk_index=2,
            timestamp_sec=6.0,
            data=b"\x10\x00" * 24000,
            duration_sec=3.0,
            sample_rate=16000,
            channels=1,
            rms_energy=0.05,
            has_speech=True,
        )
        score = scorer.score_chunk(
            chunk,
            call_context={"unknown_number": True, "claims_relative": True}
        )
        
        self.assertEqual(score.tier, "RED")
        self.assertGreaterEqual(score.risk, 0.70)
        self.assertEqual(score.prompt, "ask_for_code")
        self.assertIn("authority", score.reasons)
        self.assertIn("secrecy", score.reasons)
        self.assertIn("financial", score.reasons)
        self.assertIn("unknown_number", score.reasons)

    def test_stream_scorer_silence_chunk(self) -> None:
        scorer = StreamScorer()
        chunk = AudioChunk(
            chunk_index=0,
            timestamp_sec=0.0,
            data=b"\x00\x00" * 16000,
            duration_sec=1.0,
            sample_rate=16000,
            channels=1,
            rms_energy=0.001,
            has_speech=False,
        )
        score = scorer.score_chunk(chunk)
        self.assertEqual(score.tier, "GREEN")
        self.assertLess(score.risk, 0.10)


if __name__ == "__main__":
    unittest.main()
