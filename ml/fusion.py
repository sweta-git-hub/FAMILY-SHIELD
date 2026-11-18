"""Multimodal Logistic Fusion Engine for Family Voice Shield.

Calibrates and fuses:
1. s_a in [0.0, 1.0]: Acoustic synthetic speech / voice clone score (Phase 6)
2. s_t in [0.0, 1.0]: Semantic scam language score (Noisy-OR, Phase 5)
3. s_c in [0.0, 1.0]: Call context risk score (unknown caller, relationship claim)

Implements a generalized logistic regression with logit transformations and
fail-safe critical threat overrides ensuring high-confidence alarms cannot be
dampened by benign signals in other modalities.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class FusionResult:
    """Output of calibrated multimodal risk fusion."""
    fused_risk: float                 # Calibrated composite scam probability [0.0 - 1.0]
    logit_score: float                # Pre-sigmoid logit z
    dominant_modality: str            # Modality contributing greatest risk ('acoustic', 'semantic', 'context')
    is_critical_override: bool        # True if single modality triggered fail-safe RED threshold
    component_scores: Dict[str, float]# Individual component scores (s_a, s_t, s_c)

    def to_dict(self) -> Dict[str, object]:
        return {
            "fused_risk": round(self.fused_risk, 4),
            "logit_score": round(self.logit_score, 4),
            "dominant_modality": self.dominant_modality,
            "is_critical_override": self.is_critical_override,
            "component_scores": {k: round(v, 4) for k, v in self.component_scores.items()},
        }


class MultimodalFusionEngine:
    """Calibrated logistic fusion model for multimodal threat assessment."""

    def __init__(
        self,
        bias: float = -1.20,
        weight_acoustic: float = 1.25,
        weight_semantic: float = 1.35,
        weight_context: float = 1.50,
        critical_threshold: float = 0.70,
        epsilon: float = 1e-4,
    ) -> None:
        """
        Args:
            bias: Prior calibration offset w_0 (default -1.20 favors benign calls)
            weight_acoustic: Weight for logit(s_a)
            weight_semantic: Weight for logit(s_t)
            weight_context: Weight for linear s_c
            critical_threshold: Threshold above which single modality overrides composite
            epsilon: Numerical stability clamp for logit transformation
        """
        self.bias = bias
        self.w_a = weight_acoustic
        self.w_t = weight_semantic
        self.w_c = weight_context
        self.critical_threshold = critical_threshold
        self.epsilon = epsilon

    def _logit(self, p: float) -> float:
        """Computes numerically stable logit(p) = ln(p / (1 - p))."""
        clamped = max(self.epsilon, min(1.0 - self.epsilon, p))
        return math.log(clamped / (1.0 - clamped))

    def _sigmoid(self, z: float) -> float:
        """Computes sigmoid(z) = 1 / (1 + e^-z)."""
        if z >= 40.0:
            return 1.0
        if z <= -40.0:
            return 0.0
        return 1.0 / (1.0 + math.exp(-z))

    def fuse(self, s_a: float, s_t: float, s_c: float) -> FusionResult:
        """Fuses acoustic, semantic, and context risk scores into calibrated probability.
        
        Args:
            s_a: Acoustic synthetic speech score [0.0, 1.0]
            s_t: Semantic scam language score [0.0, 1.0]
            s_c: Context metadata score [0.0, 1.0]
            
        Returns:
            FusionResult containing calibrated fused_risk, logits, and modality attribution.
        """
        # Clamp inputs strictly to [0.0, 1.0]
        sa = max(0.0, min(1.0, float(s_a)))
        st = max(0.0, min(1.0, float(s_t)))
        sc = max(0.0, min(1.0, float(s_c)))

        # 1. Compute logistic linear combination:
        # z = w_0 + w_a * logit(s_a) + w_t * logit(s_t) + w_c * s_c
        logit_a = self._logit(sa)
        logit_t = self._logit(st)
        z = self.bias + (self.w_a * logit_a) + (self.w_t * logit_t) + (self.w_c * sc)
        calibrated_risk = self._sigmoid(z)

        # 2. Modality attribution
        # Compare contributions to determine dominant signal
        contrib_a = self.w_a * max(0.0, logit_a)
        contrib_t = self.w_t * max(0.0, logit_t)
        contrib_c = self.w_c * sc

        if contrib_a >= contrib_t and contrib_a >= contrib_c and sa > 0.30:
            dominant = "acoustic"
        elif contrib_t >= contrib_a and contrib_t >= contrib_c and st > 0.30:
            dominant = "semantic"
        elif contrib_c > 0.20:
            dominant = "context"
        else:
            dominant = "none"

        # 3. Fail-Safe Critical Override:
        # A severe synthetic voice clone (s_a >= 0.70) or severe scam threat (s_t >= 0.70)
        # must never be suppressed by benign behavior in another dimension.
        is_override = False
        if sa >= self.critical_threshold or st >= self.critical_threshold:
            max_component = max(sa, st)
            if max_component > calibrated_risk:
                calibrated_risk = max_component
                is_override = True
                if sa >= st:
                    dominant = "acoustic"
                else:
                    dominant = "semantic"

        # Strict bounding
        final_risk = max(0.0, min(1.0, calibrated_risk))

        return FusionResult(
            fused_risk=round(final_risk, 4),
            logit_score=round(z, 4),
            dominant_modality=dominant,
            is_critical_override=is_override,
            component_scores={"s_a": sa, "s_t": st, "s_c": sc},
        )
