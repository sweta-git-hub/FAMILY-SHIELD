"""
demo/scenarios.py — Realistic scripted scam and benign scenario catalog
for Family Voice Shield (FVS) evaluation.

Each scenario drives the telephony replay harness and the interactive
web simulator. Scores (s_a, s_c) and transcripts are defined to realistically
exercise the ML classifier, acoustic anti-spoof, multimodal fusion, and
alert tier hysteresis state machine.

Copyright © 2024 Family Voice Shield Project
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ScenarioChunk:
    """One 2-second telephony audio chunk for a scripted scenario."""
    chunk_index: int                   # 0-based index within the scenario
    transcript: str                    # What the caller says in this chunk
    s_a_mock: float                    # Anti-spoof score (0=natural, 1=synthetic)
    s_c: float                         # Caller-ID / cryptographic trust score
    expected_tier: str                 # "GREEN" | "AMBER" | "RED" | "REJECTED"
    language: str = "en"               # "en" | "hi" | "hinglish"
    notes: str = ""                    # Optional human-readable note


@dataclass
class CallContext:
    """Metadata about the incoming call."""
    is_unknown_number: bool = True
    claims_relative: Optional[str] = None   # e.g. "son", "daughter", "officer"
    caller_number: str = "+91-UNKNOWN"
    language: str = "hinglish"
    video_call: bool = False


@dataclass
class Scenario:
    """A complete scripted evaluation scenario."""
    scenario_id: str
    name: str
    description: str
    category: str                           # "scam" | "benign" | "edge"
    expected_final_tier: str                # GREEN | AMBER | RED | REJECTED
    call_context: CallContext
    chunks: List[ScenarioChunk]
    expected_time_to_amber_seconds: Optional[float] = None  # None for benign
    expected_time_to_red_seconds: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Scenario 1 — Fake Accident Scam
# ---------------------------------------------------------------------------

FAKE_ACCIDENT = Scenario(
    scenario_id="S1",
    name="Fake Accident – UPI Demand",
    description=(
        "Unknown caller claims to be the victim's son needing emergency help. "
        "Escalates from unfamiliar number excuse to medical/financial pressure, "
        "demanding instant UPI transfer and secrecy. "
        "Expected: AMBER by chunk-2 (t=4s, SLA ≤ 8s), RED by chunk-3 (t=6s)."
    ),
    category="scam",
    expected_final_tier="RED",
    expected_time_to_amber_seconds=4.0,
    expected_time_to_red_seconds=6.0,
    tags=["upi", "fake-accident", "hindi", "urgency", "voice-clone"],
    call_context=CallContext(
        is_unknown_number=True,
        claims_relative="son",
        caller_number="+91-9800000001",
        language="hi",
    ),
    chunks=[
        ScenarioChunk(
            chunk_index=0,
            transcript="Hello mummy, main aapka beta bol raha hoon, phone suniye.",
            s_a_mock=0.12,
            s_c=0.05,
            expected_tier="GREEN",
            language="hi",
            notes="Opening greeting: claims relative identity, low acoustic spoof",
        ),
        ScenarioChunk(
            chunk_index=1,
            transcript="Mummy ek zaroori baat hai, problem ho gayi hai.",
            s_a_mock=0.18,
            s_c=0.05,
            expected_tier="GREEN",
            language="hi",
            notes="Vague problem mention: stays in GREEN tier",
        ),
        ScenarioChunk(
            chunk_index=2,
            transcript="Mera naya number hai, abhi urgent baat karni hai.",
            s_a_mock=0.56,
            s_c=0.05,
            expected_tier="AMBER",
            language="hi",
            notes="Device excuse + urgency cues + acoustic artifacts -> escalates to AMBER (t=4s)",
        ),
        ScenarioChunk(
            chunk_index=3,
            transcript="Dost ka phone hai, turant paise transfer karne hain.",
            s_a_mock=0.58,
            s_c=0.05,
            expected_tier="RED",
            language="hi",
            notes="Financial transfer command + device excuse -> escalates to RED (t=6s)",
        ),
        ScenarioChunk(
            chunk_index=4,
            transcript="Fifty thousand chahiye abhi, UPI transfer the money right now.",
            s_a_mock=0.65,
            s_c=0.05,
            expected_tier="RED",
            language="hi",
            notes="Explicit UPI amount and immediate deadline -> sustained RED",
        ),
        ScenarioChunk(
            chunk_index=5,
            transcript="Please kisi ko mat batana, don't tell anyone, turant transfer the money.",
            s_a_mock=0.70,
            s_c=0.05,
            expected_tier="RED",
            language="hi",
            notes="Isolation/secrecy demand + high acoustic synthetic score -> confirmed RED",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Scenario 2 — Digital Arrest Scam
# ---------------------------------------------------------------------------

DIGITAL_ARREST = Scenario(
    scenario_id="S2",
    name="Digital Arrest – CBI Impersonation",
    description=(
        "Caller poses as law enforcement/courier authority investigating a financial crime. "
        "Threatens victim with digital arrest, isolation ('do not disconnect'), and demands "
        "immediate 'security deposit' transfer. "
        "Expected: AMBER at chunk-0 (t=0s), RED by chunk-1 (t=2s, SLA ≤ 4s)."
    ),
    category="scam",
    expected_final_tier="RED",
    expected_time_to_amber_seconds=0.0,
    expected_time_to_red_seconds=2.0,
    tags=["digital-arrest", "cbi", "aadhaar", "authority-impersonation"],
    call_context=CallContext(
        is_unknown_number=True,
        claims_relative=None,
        caller_number="+91-1100000000",
        language="en",
    ),
    chunks=[
        ScenarioChunk(
            chunk_index=0,
            transcript="Notice regarding courier delivery. We need verification right now.",
            s_a_mock=0.56,
            s_c=0.03,
            expected_tier="AMBER",
            language="en",
            notes="Urgency cue with unknown caller -> immediate AMBER (t=0s)",
        ),
        ScenarioChunk(
            chunk_index=1,
            transcript="This is CBI officer Sharma. Your Aadhaar number has been flagged for money laundering.",
            s_a_mock=0.60,
            s_c=0.03,
            expected_tier="RED",
            language="en",
            notes="High-weight authority impersonation -> escalates to RED (t=2s)",
        ),
        ScenarioChunk(
            chunk_index=2,
            transcript="You are under digital arrest. Transfer the money immediately, two lakh rupees deposit.",
            s_a_mock=0.65,
            s_c=0.03,
            expected_tier="RED",
            language="en",
            notes="Digital arrest coercion + large financial deposit demand -> sustained RED",
        ),
        ScenarioChunk(
            chunk_index=3,
            transcript="Do not disconnect. Stay on the line or police will arrive right now.",
            s_a_mock=0.65,
            s_c=0.03,
            expected_tier="RED",
            language="en",
            notes="Isolation command ('do not disconnect') + police threat -> confirmed RED",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Scenario 3 — Benign Family Call
# ---------------------------------------------------------------------------

BENIGN_FAMILY_CALL = Scenario(
    scenario_id="S3",
    name="Benign Family – Weekend Chat",
    description=(
        "Verified daughter calls from a known contact number to chat about weekend plans. "
        "Acoustic features exhibit natural human variability (low s_a). "
        "No coercive or financial indicators in speech. "
        "Expected: GREEN throughout all chunks."
    ),
    category="benign",
    expected_final_tier="GREEN",
    expected_time_to_amber_seconds=None,
    expected_time_to_red_seconds=None,
    tags=["benign", "family", "verified", "green"],
    call_context=CallContext(
        is_unknown_number=False,
        claims_relative="daughter",
        caller_number="+91-9811111111",
        language="hi",
    ),
    chunks=[
        ScenarioChunk(
            chunk_index=0,
            transcript="Mummy! Kya kar rahi ho? Sab theek hai?",
            s_a_mock=0.08,
            s_c=0.95,
            expected_tier="GREEN",
            language="hi",
            notes="Warm family greeting, low acoustic score, high caller trust",
        ),
        ScenarioChunk(
            chunk_index=1,
            transcript="Weekend pe ghar aana chahti hoon. Papa ke saath baat karo.",
            s_a_mock=0.07,
            s_c=0.95,
            expected_tier="GREEN",
            language="hi",
            notes="Social plans discussion -> GREEN maintained",
        ),
        ScenarioChunk(
            chunk_index=2,
            transcript="Aur haan — Priya bhi aa sakti hai. Khana banao na mummy.",
            s_a_mock=0.09,
            s_c=0.95,
            expected_tier="GREEN",
            language="hi",
            notes="Casual conversation -> GREEN maintained",
        ),
        ScenarioChunk(
            chunk_index=3,
            transcript="Okay bye! Love you mummy. See you Saturday!",
            s_a_mock=0.06,
            s_c=0.95,
            expected_tier="GREEN",
            language="hi",
            notes="Warm farewell -> stays GREEN throughout call",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Scenario 4 — Relay Attack Defense
# ---------------------------------------------------------------------------

RELAY_ATTACK = Scenario(
    scenario_id="S4",
    name="Relay Attack Defense – Stale Session Replay",
    description=(
        "Attacker intercepts and attempts to replay a legitimate family voice verification "
        "challenge response from a prior session. The cryptographic directional key verification "
        "detects the expired time step and reused session nonce. "
        "Call is terminated at the handshake layer before ML stream scoring. "
        "Expected: REJECTED."
    ),
    category="edge",
    expected_final_tier="REJECTED",
    expected_time_to_amber_seconds=None,
    expected_time_to_red_seconds=None,
    tags=["relay-attack", "cryptographic", "replay", "security"],
    call_context=CallContext(
        is_unknown_number=False,       # Caller ID was spoofed
        claims_relative="son",
        caller_number="+91-9811111112",
        language="en",
    ),
    chunks=[
        ScenarioChunk(
            chunk_index=0,
            transcript="[CRYPTOGRAPHIC GATEWAY: Stale nonce detected — replayed session token rejected]",
            s_a_mock=0.0,
            s_c=0.0,
            expected_tier="REJECTED",
            language="en",
            notes="Replay attack rejected: directional HMAC mismatch or expired TOTP counter",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Scenario 5 — Duress Call
# ---------------------------------------------------------------------------

DURESS_CALL = Scenario(
    scenario_id="S5",
    name="Duress Call – Silent Emergency Notification",
    description=(
        "Legitimate family member is physically coerced by an attacker standing nearby. "
        "The victim speaks naturally while covertly embedding the pre-registered family duress "
        "keyword ('Raju'). FVS keeps the UI in GREEN to maintain victim safety, while "
        "instantly transmitting an HMAC-signed emergency SMS alert to trusted family guardians. "
        "Expected: Displayed tier stays GREEN, emergency notification dispatched."
    ),
    category="edge",
    expected_final_tier="GREEN",
    expected_time_to_amber_seconds=None,
    expected_time_to_red_seconds=None,
    tags=["duress", "emergency", "stealth-alert", "safety"],
    call_context=CallContext(
        is_unknown_number=False,
        claims_relative="daughter",
        caller_number="+91-9811111113",
        language="en",
    ),
    chunks=[
        ScenarioChunk(
            chunk_index=0,
            transcript="Hi mummy, I am fine, don't worry about me at all.",
            s_a_mock=0.09,
            s_c=0.90,
            expected_tier="GREEN",
            language="en",
            notes="Normal greeting — attacker suspects nothing",
        ),
        ScenarioChunk(
            chunk_index=1,
            transcript="I just wanted to say I love you all, please take care of Raju.",
            s_a_mock=0.10,
            s_c=0.90,
            expected_tier="GREEN",
            language="en",
            notes="Duress keyword 'Raju' uttered -> triggers silent emergency broadcast",
        ),
        ScenarioChunk(
            chunk_index=2,
            transcript="Everything is totally fine here, I will call you tomorrow.",
            s_a_mock=0.08,
            s_c=0.90,
            expected_tier="GREEN",
            language="en",
            notes="Conversation safely terminated without alerting aggressor",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

SCENARIO_CATALOG: List[Scenario] = [
    FAKE_ACCIDENT,
    DIGITAL_ARREST,
    BENIGN_FAMILY_CALL,
    RELAY_ATTACK,
    DURESS_CALL,
]

SCENARIO_BY_ID = {s.scenario_id: s for s in SCENARIO_CATALOG}
SCENARIO_BY_NAME = {s.name: s for s in SCENARIO_CATALOG}


def get_scenario(identifier: str) -> Optional[Scenario]:
    """Return a scenario by ID (e.g. 'S1') or name substring (case-insensitive)."""
    if identifier in SCENARIO_BY_ID:
        return SCENARIO_BY_ID[identifier]
    lower = identifier.lower()
    for s in SCENARIO_CATALOG:
        if lower in s.name.lower() or lower in s.scenario_id.lower():
            return s
    return None


def list_scenarios() -> List[dict]:
    """Return a JSON-serialisable summary list of all scenarios."""
    return [
        {
            "id": s.scenario_id,
            "name": s.name,
            "category": s.category,
            "expected_final_tier": s.expected_final_tier,
            "num_chunks": len(s.chunks),
            "tags": s.tags,
            "expected_time_to_amber_seconds": s.expected_time_to_amber_seconds,
            "expected_time_to_red_seconds": s.expected_time_to_red_seconds,
        }
        for s in SCENARIO_CATALOG
    ]


if __name__ == "__main__":
    import json
    print("=== Family Voice Shield — Scenario Catalog ===\n")
    for info in list_scenarios():
        print(json.dumps(info, indent=2))
        print()
