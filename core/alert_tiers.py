"""Alert Tier State Machine and Hysteresis Engine for Family Voice Shield.

Manages dynamic call risk transitions between:
- GREEN: Normal call (< 0.40)
- AMBER: Suspicious call (0.40 - 0.70)
- RED: High-risk scam / voice clone (>= 0.70)

Features:
1. Asymmetric hysteresis debouncing: Fast escalation (instantaneous trigger on high risk)
   and damped de-escalation (requires sustained low risk to prevent UI flapping)
2. Bilingual spoken prompts (English & Hindi) for elderly accessibility
3. Emergency notification payload generation with HMAC tamper protection
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class AlertTier(str, Enum):
    """Call risk alert tiers."""
    GREEN = "GREEN"   # Normal benign conversation
    AMBER = "AMBER"   # Elevated suspicion; recommend asking for family code
    RED = "RED"       # Critical threat; demand rotating family code / alert family


@dataclass(frozen=True)
class AlertTransition:
    """Represents a state machine transition event."""
    from_tier: AlertTier
    to_tier: AlertTier
    timestamp: float
    trigger_risk: float
    reasons: List[str]
    is_escalation: bool


@dataclass(frozen=True)
class EmergencyNotification:
    """Signed emergency alert payload dispatched to registered family members."""
    notification_id: str
    timestamp: float
    tier: str
    risk_score: float
    dominant_modality: str
    reasons: List[str]
    masked_target_phone: str
    action_required: str
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "notification_id": self.notification_id,
            "timestamp": self.timestamp,
            "tier": self.tier,
            "risk_score": round(self.risk_score, 4),
            "dominant_modality": self.dominant_modality,
            "reasons": self.reasons,
            "masked_target_phone": self.masked_target_phone,
            "action_required": self.action_required,
            "signature": self.signature,
        }


class AlertStateMachine:
    """Hysteresis state machine governing alert tiers and debouncing."""

    def __init__(
        self,
        amber_threshold: float = 0.40,
        red_threshold: float = 0.70,
        amber_deescalate_threshold: float = 0.32,
        red_deescalate_threshold: float = 0.60,
        deescalate_patience_chunks: int = 2,
        secret_key: bytes = b"fvs-alert-hmac-key-v1",
    ) -> None:
        """
        Args:
            amber_threshold: Threshold to escalate to AMBER
            red_threshold: Threshold to escalate to RED
            amber_deescalate_threshold: Lower bound required to fall back from AMBER to GREEN
            red_deescalate_threshold: Lower bound required to fall back from RED to AMBER
            deescalate_patience_chunks: Number of consecutive low chunks required to de-escalate
            secret_key: Secret key used to sign emergency broadcast notifications
        """
        self.amber_thresh = amber_threshold
        self.red_thresh = red_threshold
        self.amber_deescalate = amber_deescalate_threshold
        self.red_deescalate = red_deescalate_threshold
        self.deescalate_patience = deescalate_patience_chunks
        self.secret_key = secret_key

        self.current_tier = AlertTier.GREEN
        self.deescalate_counter = 0
        self.history: List[AlertTransition] = []
        self.consecutive_red_chunks = 0

    def update(
        self,
        fused_risk: float,
        reasons: Optional[List[str]] = None,
        timestamp: Optional[float] = None,
    ) -> Tuple[AlertTier, Optional[AlertTransition]]:
        """Processes a new chunk risk score and returns updated tier and transition event if any."""
        now = timestamp if timestamp is not None else time.time()
        active_reasons = list(reasons or [])
        prev_tier = self.current_tier
        next_tier = self.current_tier

        # 1. Fast Escalation (Instantaneous protection)
        if fused_risk >= self.red_thresh:
            next_tier = AlertTier.RED
            self.deescalate_counter = 0
            self.consecutive_red_chunks += 1
        elif fused_risk >= self.amber_thresh:
            if self.current_tier == AlertTier.GREEN:
                next_tier = AlertTier.AMBER
                self.deescalate_counter = 0
                self.consecutive_red_chunks = 0
            elif self.current_tier == AlertTier.RED:
                # Potential de-escalation from RED
                if fused_risk < self.red_deescalate:
                    self.deescalate_counter += 1
                    if self.deescalate_counter >= self.deescalate_patience:
                        next_tier = AlertTier.AMBER
                        self.deescalate_counter = 0
                        self.consecutive_red_chunks = 0
                else:
                    self.deescalate_counter = 0
                    self.consecutive_red_chunks += 1
        else:
            # Low risk (< amber_thresh)
            if self.current_tier == AlertTier.GREEN:
                self.deescalate_counter = 0
                self.consecutive_red_chunks = 0
            elif self.current_tier == AlertTier.AMBER:
                if fused_risk < self.amber_deescalate:
                    self.deescalate_counter += 1
                    if self.deescalate_counter >= self.deescalate_patience:
                        next_tier = AlertTier.GREEN
                        self.deescalate_counter = 0
                        self.consecutive_red_chunks = 0
            elif self.current_tier == AlertTier.RED:
                # Severe de-escalation step down to AMBER first
                if fused_risk < self.red_deescalate:
                    self.deescalate_counter += 1
                    if self.deescalate_counter >= self.deescalate_patience:
                        next_tier = AlertTier.AMBER
                        self.deescalate_counter = 0
                        self.consecutive_red_chunks = 0

        self.current_tier = next_tier

        # 2. Check for tier change event
        transition: Optional[AlertTransition] = None
        if next_tier != prev_tier:
            is_escalation = (
                (prev_tier == AlertTier.GREEN and next_tier in (AlertTier.AMBER, AlertTier.RED))
                or (prev_tier == AlertTier.AMBER and next_tier == AlertTier.RED)
            )
            transition = AlertTransition(
                from_tier=prev_tier,
                to_tier=next_tier,
                timestamp=now,
                trigger_risk=fused_risk,
                reasons=active_reasons,
                is_escalation=is_escalation,
            )
            self.history.append(transition)

        return self.current_tier, transition

    def get_prompt_action(self) -> str:
        """Returns standard prompt command for current tier."""
        if self.current_tier == AlertTier.GREEN:
            return "normal"
        return "ask_for_code"

    def get_spoken_advisory(self, lang: str = "hi") -> str:
        """Returns localized accessibility speech guidance for current tier."""
        if self.current_tier == AlertTier.GREEN:
            return "कॉल सामान्य है" if lang == "hi" else "Call appears normal"
        elif self.current_tier == AlertTier.AMBER:
            return "सतर्क रहें: कृपया परिवार का 6-अंकों का कोड मांगें" if lang == "hi" else "Caution: Please ask caller for the 6-digit family code"
        else:
            return "चेतावनी! संभावित आवाज क्लोन या धोखाधड़ी। तुरंत कोड मांगें या फोन काट दें!" if lang == "hi" else "Warning! Potential voice clone or scam. Demand family code or hang up immediately!"

    def generate_emergency_notification(
        self,
        target_phone: str,
        fused_risk: float,
        dominant_modality: str,
        reasons: List[str],
    ) -> EmergencyNotification:
        """Constructs an HMAC-signed emergency payload to notify family members."""
        now = time.time()
        # Mask phone number per Rule 7 privacy rules (e.g. +91 98*** **321)
        clean = "".join(ch for ch in target_phone if ch.isdigit() or ch == "+")
        if len(clean) >= 8:
            masked = clean[:5] + "***" + clean[-3:]
        else:
            masked = "***"

        nid = hashlib.sha256(f"{target_phone}:{now}:{fused_risk}".encode()).hexdigest()[:16]
        action = "Guardian is currently on a suspicious high-risk call. Verify immediately via direct call or emergency contact."

        # Sign with HMAC-SHA256
        sig_data = f"{nid}:{now}:{self.current_tier.value}:{round(fused_risk, 4)}:{masked}".encode()
        signature = hmac.new(self.secret_key, sig_data, hashlib.sha256).hexdigest()

        return EmergencyNotification(
            notification_id=nid,
            timestamp=now,
            tier=self.current_tier.value,
            risk_score=fused_risk,
            dominant_modality=dominant_modality,
            reasons=reasons,
            masked_target_phone=masked,
            action_required=action,
            signature=signature,
        )
