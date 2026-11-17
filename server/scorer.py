"""Decision scorer for Family Voice Shield audio streaming.

In Phase 5, integrates real semantic scam classification (ml.scam_classifier)
and Speech-To-Text inference (ml.stt_engine).
Acoustic anti-spoofing score s_a remains mock pending Phase 6 AASIST integration.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ml.scam_classifier import ClassificationResult, NoisyOrScamClassifier
from ml.stt_engine import BaseSTTEngine, create_stt_engine
from server.chunker import AudioChunk


@dataclass(frozen=True)
class RiskScore:
    """Contract-compliant risk score frame per docs/07_API_CONTRACTS.md."""
    type: str = "score"
    t: float = 0.0
    s_a: float = 0.0      # Acoustic synthetic score [0.0 - 1.0] (Mock until Phase 6)
    s_t: float = 0.0      # Semantic scam language score [0.0 - 1.0] (Real Phase 5)
    s_c: float = 0.0      # Call context risk score [0.0 - 1.0]
    risk: float = 0.0     # Fused risk probability [0.0 - 1.0]
    tier: str = "GREEN"   # GREEN (<0.40), AMBER (0.40 - 0.70), RED (>0.70)
    reasons: List[str] = field(default_factory=list)
    prompt: str = "normal"
    mock: bool = False    # Real semantic scoring active

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "t": round(self.t, 2),
            "s_a": round(self.s_a, 4),
            "s_t": round(self.s_t, 4),
            "s_c": round(self.s_c, 4),
            "risk": round(self.risk, 4),
            "tier": self.tier,
            "reasons": self.reasons,
            "prompt": self.prompt,
            "mock": self.mock,
        }


class StreamScorer:
    """Production stream scorer integrating STT and Noisy-OR scam classifier."""

    def __init__(
        self,
        stt_engine: Optional[BaseSTTEngine] = None,
        classifier: Optional[NoisyOrScamClassifier] = None,
        baseline_acoustic_risk: float = 0.10,
    ) -> None:
        self.stt_engine = stt_engine or create_stt_engine()
        self.classifier = classifier or NoisyOrScamClassifier()
        self.baseline_acoustic_risk = baseline_acoustic_risk

    def score_chunk(self, chunk: AudioChunk, call_context: Dict[str, Any] | None = None) -> RiskScore:
        """Evaluates an audio chunk through STT and semantic classifier."""
        context = call_context or {}
        unknown_number = bool(context.get("unknown_number", False))
        claims_relative = bool(context.get("claims_relative", False))
        caller_lang = context.get("lang", "hi")

        # Context score
        s_c = 0.25 if (unknown_number and claims_relative) else (0.15 if unknown_number else 0.05)

        if not chunk.has_speech:
            return RiskScore(
                t=chunk.timestamp_sec,
                s_a=0.01,
                s_t=0.02,
                s_c=s_c,
                risk=round(s_c * 0.5, 4),
                tier="GREEN",
                reasons=[],
                prompt="normal",
                mock=False,
            )

        # 1. Transcribe audio in memory (Rule 7: zero disk persistence)
        pcm_bytes = getattr(chunk, "data", getattr(chunk, "pcm_data", b""))
        stt_res = self.stt_engine.transcribe_pcm(pcm_bytes, sample_rate=16000, lang=caller_lang)
        transcript = stt_res.text

        # Semantic classification with Noisy-OR
        clf_res = self.classifier.classify_text(transcript)
        s_t = clf_res.s_t

        # Acoustic score: MOCK until Phase 6
        s_a = self.baseline_acoustic_risk

        # Composite fused risk:
        # In Phase 5, semantic scam detection is the primary active ML signal.
        # If s_t indicates a critical scam (>=0.70), composite risk reflects critical level.
        fused_risk = max(
            s_t,
            max(0.0, min(1.0, 0.60 * s_t + 0.25 * s_a + 0.15 * s_c))
        )

        reasons: List[str] = []
        for cat in clf_res.matched_categories:
            reasons.append(cat.value)

        if unknown_number:
            reasons.append("unknown_number")
        if claims_relative:
            reasons.append("claims_relative")

        if fused_risk >= 0.70:
            tier = "RED"
            prompt = "ask_for_code"
        elif fused_risk >= 0.40:
            tier = "AMBER"
            prompt = "ask_for_code"
        else:
            tier = "GREEN"
            prompt = "normal"

        return RiskScore(
            t=chunk.timestamp_sec,
            s_a=s_a,
            s_t=s_t,
            s_c=s_c,
            risk=fused_risk,
            tier=tier,
            reasons=reasons,
            prompt=prompt,
            mock=stt_res.is_mock,
        )


# Backward-compatible alias for existing tests
class MockScorer(StreamScorer):
    """MOCK: Retained for explicit testing or backward compatibility."""
    def __init__(self, baseline_risk: float = 0.12) -> None:
        super().__init__(baseline_acoustic_risk=baseline_risk)
