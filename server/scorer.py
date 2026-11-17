"""Decision scorer for Family Voice Shield audio streaming.

In Phase 5, integrated real semantic scam classification (ml.scam_classifier)
and Speech-To-Text inference (ml.stt_engine).
In Phase 6, integrates real acoustic anti-spoofing and synthetic speech detection
(ml.antispoof_engine).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ml.antispoof_engine import BaseAntiSpoofEngine, create_antispoof_engine
from ml.scam_classifier import ClassificationResult, NoisyOrScamClassifier
from ml.stt_engine import BaseSTTEngine, create_stt_engine
from server.chunker import AudioChunk


@dataclass(frozen=True)
class RiskScore:
    """Contract-compliant risk score frame per docs/07_API_CONTRACTS.md."""
    type: str = "score"
    t: float = 0.0
    s_a: float = 0.0      # Acoustic synthetic score [0.0 - 1.0] (Real Phase 6)
    s_t: float = 0.0      # Semantic scam language score [0.0 - 1.0] (Real Phase 5)
    s_c: float = 0.0      # Call context risk score [0.0 - 1.0]
    risk: float = 0.0     # Fused risk probability [0.0 - 1.0]
    tier: str = "GREEN"   # GREEN (<0.40), AMBER (0.40 - 0.70), RED (>0.70)
    reasons: List[str] = field(default_factory=list)
    prompt: str = "normal"
    mock: bool = False    # Real acoustic & semantic scoring active

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
    """Production stream scorer integrating STT, Noisy-OR scam classifier, and acoustic anti-spoofing."""

    def __init__(
        self,
        stt_engine: Optional[BaseSTTEngine] = None,
        classifier: Optional[NoisyOrScamClassifier] = None,
        antispoof_engine: Optional[BaseAntiSpoofEngine] = None,
        baseline_acoustic_risk: float = 0.10,
        is_mock: bool = False,
    ) -> None:
        self.stt_engine = stt_engine or create_stt_engine()
        self.classifier = classifier or NoisyOrScamClassifier()
        self.antispoof_engine = antispoof_engine or create_antispoof_engine()
        self.baseline_acoustic_risk = baseline_acoustic_risk
        self.is_mock = is_mock

    def score_chunk(self, chunk: AudioChunk, call_context: Dict[str, Any] | None = None) -> RiskScore:
        """Evaluates an audio chunk through STT, semantic classifier, and acoustic anti-spoof."""
        context = call_context or {}
        unknown_number = bool(context.get("unknown_number", False))
        claims_relative = bool(context.get("claims_relative", False))
        caller_lang = context.get("lang", "hi")

        # Context score
        s_c = 0.25 if (unknown_number and claims_relative) else (0.15 if unknown_number else 0.05)

        pcm_bytes = getattr(chunk, "data", getattr(chunk, "pcm_data", b""))

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
                mock=self.is_mock,
            )

        # 1. Transcribe audio in memory (Rule 7: zero disk persistence)
        stt_res = self.stt_engine.transcribe_pcm(pcm_bytes, sample_rate=16000, lang=caller_lang)
        transcript = stt_res.text

        # 2. Semantic classification with Noisy-OR
        clf_res = self.classifier.classify_text(transcript)
        s_t = clf_res.s_t

        # 3. Acoustic anti-spoof / synthetic voice evaluation (Phase 6)
        as_res = self.antispoof_engine.score_audio(pcm_bytes, sample_rate=16000)
        s_a = as_res.s_a

        # 4. Composite fused risk calculation:
        # Either severe acoustic spoofing (s_a >= 0.70) or severe scam intent (s_t >= 0.70)
        # immediately elevates the composite risk to critical RED tier.
        weighted_risk = 0.45 * s_t + 0.40 * s_a + 0.15 * s_c
        fused_risk = max(
            s_t if s_t >= 0.70 else 0.0,
            s_a if s_a >= 0.70 else 0.0,
            max(0.0, min(1.0, weighted_risk))
        )

        reasons: List[str] = []
        for cat in clf_res.matched_categories:
            reasons.append(cat.value)

        for artifact in as_res.artifacts_detected:
            reasons.append(artifact)

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

        is_mock_eval = self.is_mock or bool(getattr(stt_res, "is_mock", False) and getattr(as_res, "is_mock", False))

        return RiskScore(
            t=chunk.timestamp_sec,
            s_a=s_a,
            s_t=s_t,
            s_c=s_c,
            risk=round(fused_risk, 4),
            tier=tier,
            reasons=reasons,
            prompt=prompt,
            mock=is_mock_eval,
        )


# Backward-compatible alias for existing tests
class MockScorer(StreamScorer):
    """MOCK: Retained for explicit testing or backward compatibility."""
    def __init__(self, baseline_risk: float = 0.12) -> None:
        super().__init__(baseline_acoustic_risk=baseline_risk, is_mock=True)

