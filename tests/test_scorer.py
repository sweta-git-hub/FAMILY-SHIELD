"""Unit tests for MockScorer (MOCK)."""

import unittest
from server.chunker import AudioChunk
from server.scorer import MockScorer, RiskScore


class TestMockScorer(unittest.TestCase):

    def setUp(self) -> None:
        self.scorer = MockScorer()

    def _make_chunk(self, has_speech: bool = True, timestamp: float = 3.0) -> AudioChunk:
        return AudioChunk(
            chunk_index=0,
            timestamp_sec=timestamp,
            data=b"\x00" * 96000,
            duration_sec=3.0,
            sample_rate=16000,
            channels=1,
            rms_energy=0.05 if has_speech else 0.0,
            has_speech=has_speech,
        )

    def test_mock_scorer_contract_format(self) -> None:
        chunk = self._make_chunk(has_speech=True, timestamp=3.0)
        score = self.scorer.score_chunk(chunk)

        self.assertIsInstance(score, RiskScore)
        d = score.to_dict()

        self.assertEqual(d["type"], "score")
        self.assertEqual(d["t"], 3.0)
        self.assertTrue(d["mock"])  # Rule 0.5 compliance
        self.assertIn("s_a", d)
        self.assertIn("s_t", d)
        self.assertIn("s_c", d)
        self.assertIn("risk", d)
        self.assertIn("tier", d)
        self.assertIn("prompt", d)
        self.assertIn("reasons", d)

    def test_silence_chunk_scores_green(self) -> None:
        chunk = self._make_chunk(has_speech=False, timestamp=3.0)
        score = self.scorer.score_chunk(chunk)

        self.assertEqual(score.tier, "GREEN")
        self.assertEqual(score.prompt, "normal")
        self.assertLess(score.risk, 0.40)

    def test_context_influences_risk(self) -> None:
        chunk = self._make_chunk(has_speech=True, timestamp=3.0)

        # Baseline context
        score_base = self.scorer.score_chunk(chunk, call_context={})

        # High risk context: unknown number claiming to be relative
        score_ctx = self.scorer.score_chunk(chunk, call_context={
            "unknown_number": True,
            "claims_relative": True
        })

        self.assertGreater(score_ctx.s_c, score_base.s_c)
        self.assertGreaterEqual(score_ctx.risk, score_base.risk)


if __name__ == "__main__":
    unittest.main()
