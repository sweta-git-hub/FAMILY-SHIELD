"""Dummy decision scorer for Family Voice Shield audio streaming.

Labelled MOCK per Rule 0.5: Returns contract-compliant risk scores and tiers
prior to integration of real Whisper STT (Phase 5) and AASIST anti-spoof (Phase 6).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from server.chunker import AudioChunk


@dataclass(frozen=True)
class RiskScore:
    """Contract-compliant risk score frame per docs/07_API_CONTRACTS.md."""
    type: str = "score"
    t: float = 0.0
    s_a: float = 0.0      # Acoustic synthetic score [0.0 - 1.0] (Phase 6)
    s_t: float = 0.0      # Semantic scam language score [0.0 - 1.0] (Phase 5)
    s_c: float = 0.0      # Call context risk score [0.0 - 1.0]
    risk: float = 0.0     # Fused risk probability [0.0 - 1.0]
    tier: str = "GREEN"   # GREEN (<0.40), AMBER (0.40 - 0.70), RED (>0.70)
    reasons: List[str] = field(default_factory=list)
    prompt: str = "normal"
    mock: bool = True     # Explicit MOCK indicator per Rule 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "t": self.t,
            "s_a": self.s_a,
            "s_t": self.s_t,
            "s_c": self.s_c,
            "risk": self.risk,
            "tier": self.tier,
            "reasons": self.reasons,
            "prompt": self.prompt,
            "mock": self.mock,
        }


class MockScorer:
    """MOCK: Generates deterministic contract-compliant scores for Phase 4 streaming."""

    def __init__(self, baseline_risk: float = 0.12) -> None:
        self.baseline_risk = baseline_risk

    def score_chunk(self, chunk: AudioChunk, call_context: Dict[str, Any] | None = None) -> RiskScore:
        """Evaluates an audio chunk and optional context, returning a structured RiskScore."""
        context = call_context or {}
        unknown_number = bool(context.get("unknown_number", False))
        claims_relative = bool(context.get("claims_relative", False))

        # Context baseline
        s_c = 0.20 if (unknown_number and claims_relative) else 0.05

        if not chunk.has_speech:
            # Silence or background hiss: minimal risk
            return RiskScore(
                t=chunk.timestamp_sec,
                s_a=0.01,
                s_t=0.01,
                s_c=round(s_c, 2),
                risk=round(s_c * 0.5, 2),
                tier="GREEN",
                reasons=[],
                prompt="normal",
                mock=True,
            )

        # Baseline mock risk for active speech
        s_a = 0.15
        s_t = 0.10
        fused_risk = round(0.4 * s_a + 0.4 * s_t + 0.2 * s_c, 2)

        tier = "GREEN"
        prompt = "normal"
        reasons = []

        if fused_risk >= 0.70:
            tier = "RED"
            prompt = "ask_for_code"
            reasons = ["high_risk_composite"]
        elif fused_risk >= 0.40:
            tier = "AMBER"
            prompt = "ask_for_code"
            reasons = ["elevated_risk"]

        return RiskScore(
            t=chunk.timestamp_sec,
            s_a=s_a,
            s_t=s_t,
            s_c=round(s_c, 2),
            risk=fused_risk,
            tier=tier,
            reasons=reasons,
            prompt=prompt,
            mock=True,
        )
