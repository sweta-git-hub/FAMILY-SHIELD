"""Probabilistic Noisy-OR Scam Intent Classifier.

Computes calibrated semantic scam risk probability s_t in [0.0, 1.0]
from extracted scam categories using a causal Noisy-OR Bayesian formulation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from ml.scam_lexicon import CATEGORY_PRIORS, ScamCategory, ScamLexicon


@dataclass(frozen=True)
class ClassificationResult:
    """Detailed output of the semantic scam classification."""
    s_t: float                                # Calibrated semantic scam score [0.0, 1.0]
    matched_categories: List[ScamCategory]    # Triggered category list
    triggers: Dict[str, List[str]]            # Category -> matched phrase substrings
    highest_risk_category: Optional[str]      # Category contributing largest risk
    leak_probability: float                   # Baseline background risk probability
    is_suspicious: bool                       # True if s_t >= 0.40 (AMBER threshold)
    is_critical: bool                         # True if s_t >= 0.70 (RED threshold)

    def to_dict(self) -> Dict[str, object]:
        return {
            "s_t": round(self.s_t, 4),
            "matched_categories": [cat.value for cat in self.matched_categories],
            "triggers": self.triggers,
            "highest_risk_category": self.highest_risk_category,
            "leak_probability": self.leak_probability,
            "is_suspicious": self.is_suspicious,
            "is_critical": self.is_critical,
        }


class NoisyOrScamClassifier:
    """Probabilistic scam classifier implementing the Noisy-OR formulation.
    
    Given a set of active scam indicators X = {x_1, x_2, ... x_n}, the probability
    of an ongoing scam S is:
    
        P(S = 1 | X) = 1 - (1 - p_0) * prod_{i: x_i = 1} (1 - p_i)
        
    where:
        - p_0 is the spontaneous background leak probability (baseline false positive rate)
        - p_i is the causal probability that active indicator x_i alone triggers a scam
    """

    def __init__(
        self,
        lexicon: Optional[ScamLexicon] = None,
        category_weights: Optional[Dict[ScamCategory, float]] = None,
        background_leak: float = 0.05,
    ) -> None:
        """Initializes classifier.
        
        Args:
            lexicon: ScamLexicon instance (defaults to standard bilingual lexicon).
            category_weights: Per-category causal probabilities p_i in [0.0, 1.0].
            background_leak: p_0 background probability (default 0.05).
        """
        self.lexicon = lexicon or ScamLexicon()
        self.category_weights = category_weights or CATEGORY_PRIORS
        self.background_leak = max(0.0, min(background_leak, 0.20))

    def classify_text(self, text: str) -> ClassificationResult:
        """Classifies a transcribed speech segment or accumulated text.
        
        Args:
            text: Transcribed speech text (English, Hindi, or Hinglish).
            
        Returns:
            ClassificationResult containing s_t score, matched categories, and triggers.
        """
        if not text or not text.strip():
            return ClassificationResult(
                s_t=self.background_leak,
                matched_categories=[],
                triggers={},
                highest_risk_category=None,
                leak_probability=self.background_leak,
                is_suspicious=False,
                is_critical=False,
            )

        grouped = self.lexicon.extract_categories(text)
        active_categories = list(grouped.keys())

        if not active_categories:
            # Clean conversation: baseline leak probability
            return ClassificationResult(
                s_t=self.background_leak,
                matched_categories=[],
                triggers={},
                highest_risk_category=None,
                leak_probability=self.background_leak,
                is_suspicious=False,
                is_critical=False,
            )

        # Noisy-OR computation: P(Scam) = 1 - (1 - p_0) * prod(1 - p_i)
        prod_non_trigger = 1.0 - self.background_leak
        max_pi = 0.0
        highest_cat: Optional[str] = None

        for cat in active_categories:
            pi = self.category_weights.get(cat, 0.50)
            prod_non_trigger *= (1.0 - pi)
            if pi > max_pi:
                max_pi = pi
                highest_cat = cat.value

        prob_scam = 1.0 - prod_non_trigger
        # Bound strictly in [0.0, 1.0]
        s_t = max(0.0, min(1.0, prob_scam))

        serializable_triggers = {
            cat.value: list(set(matches)) for cat, matches in grouped.items()
        }

        return ClassificationResult(
            s_t=s_t,
            matched_categories=active_categories,
            triggers=serializable_triggers,
            highest_risk_category=highest_cat,
            leak_probability=self.background_leak,
            is_suspicious=(s_t >= 0.40),
            is_critical=(s_t >= 0.70),
        )

    def score_phrases(self, phrases: List[str]) -> float:
        """Convenience method returning raw s_t float for a list of utterances."""
        combined = " ".join(phrases)
        return self.classify_text(combined).s_t
