"""Bilingual Scam Lexicon and Category Taxonomy for Family Voice Shield.

Defines regex patterns, keyword triggers, and calibrated scam probabilities
for 6 core social engineering threat categories across English, Hindi (Devanagari),
and Hinglish (Romanized Hindi).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Pattern, Set, Tuple


class ScamCategory(str, Enum):
    """Core categories of social engineering / voice clone scam tactics."""
    URGENCY = "urgency"               # Artificial time pressure
    SECRECY = "secrecy"               # Isolation from family / don't hang up
    AUTHORITY = "authority"           # Police, CBI, ED, Digital Arrest, customs
    DISTRESS = "distress"             # Accident, hospital, kidnapping, bail
    FINANCIAL = "financial"           # UPI, GPay, PhonePe, immediate fund transfer
    DEVICE_EXCUSE = "device_excuse"   # Lost phone, friend's phone, new SIM


@dataclass(frozen=True)
class LexiconEntry:
    """Individual pattern rule within the scam lexicon."""
    pattern: str
    category: ScamCategory
    weight: int                       # 1: weak (0.35), 2: medium (0.65), 3: high (0.85)
    description: str
    compiled: Pattern[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "compiled",
            re.compile(self.pattern, re.IGNORECASE | re.UNICODE),
        )


# Calibrated category default leak probabilities p_i for Noisy-OR
CATEGORY_PRIORS: Dict[ScamCategory, float] = {
    ScamCategory.AUTHORITY: 0.85,      # High specificity: police/digital arrest rarely benign in personal calls
    ScamCategory.SECRECY: 0.80,        # Demands to keep call secret or stay on line
    ScamCategory.FINANCIAL: 0.75,      # Urgent payment steering
    ScamCategory.DISTRESS: 0.70,       # Emergency claims
    ScamCategory.URGENCY: 0.55,        # Common in daily life, but adds weight when paired
    ScamCategory.DEVICE_EXCUSE: 0.50,   # "new number / lost phone" excuse
}


# Lexicon rules covering English, Hindi (Devanagari), and Romanized Hinglish
RAW_PATTERNS: List[Tuple[str, ScamCategory, int, str]] = [
    # 1. AUTHORITY & LEGAL THREATS (Digital Arrest, Police, CBI, Courts, Customs)
    (
        r"\b(digital\s*arrest|police\s*case|police\s*station|thana|cbi|ed\s*officer|customs|court\s*order|fir\s*lodged|arrest\s*warrant|crime\s*branch|narcotics|giraftaar|giraftar|hawalat|jail\s*bhej|supreme\s*court)\b",
        ScamCategory.AUTHORITY,
        3,
        "Law enforcement, arrest, or judicial coercion",
    ),
    (
        r"(डिजिटल\s*अरेस्ट|पुलिस|थाना|सीबीआई|गिरफ्तार|हवालात|जेल|वारंट|कस्टम)",
        ScamCategory.AUTHORITY,
        3,
        "Devanagari: Police, arrest, jail or customs threat",
    ),

    # 2. SECRECY & ISOLATION (Isolating victim from support network)
    (
        r"\b(don'?t\s*tell\s*(anyone|mom|dad|family|father|mother|wife|husband)|kisi\s*ko\s*mat\s*batana|kisi\s*se\s*baat\s*mat\s*karo|phone\s*mat\s*(katna|kaatna)|keep\s*this\s*secret|do\s*not\s*disconnect|stay\s*on\s*the\s*line|line\s*par\s*raho)\b",
        ScamCategory.SECRECY,
        3,
        "Direct instruction to conceal call or stay on continuous line",
    ),
    (
        r"(किसी\s*को\s*मत\s*बताना|फोन\s*मत\s*काटना|लाइन\s*पर\s*रहो|सीक्रेट\s*रखो)",
        ScamCategory.SECRECY,
        3,
        "Devanagari: Do not tell anyone or hang up",
    ),

    # 3. FINANCIAL STEERING (Immediate payment, UPI, GPay, QR code)
    (
        r"\b(upi(\s*(karo|kardo|bhejo|id|transfer|pin))?|gpay|phonepe|paytm|send\s*(money|rupees|cash|fund|funds)|transfer\s*(the\s*)?(money|funds?|rupees|cash)|scan\s*(the\s*)?qr|approve\s*(the\s*)?request|instant\s*transfer|paise\s*(bhejo|daal\s*do|transfer\s*karo)|account\s*khali)\b",
        ScamCategory.FINANCIAL,
        3,
        "Urgent digital payment, UPI, or QR scan command",
    ),
    (
        r"(यूपीआई|पैसे\s*भेजो|गूगल\s*पे|फोन\s*पे|खाते\s*में\s*डालो|क्यूआर\s*कोड)",
        ScamCategory.FINANCIAL,
        3,
        "Devanagari: UPI, Google Pay, money transfer or QR code",
    ),

    # 4. DISTRESS & EMERGENCY CLAIMS (Accident, Hospital, Kidnapping, Hostage)
    (
        r"\b(accident|hospital(ised|ized)?|emergency|serious\s*condition|icu|operation|bacha\s*lo|help\s*me\s*please|kidnap|bail\s*money|illaz|khatre\s*mein)\b",
        ScamCategory.DISTRESS,
        2,
        "Accident, medical emergency, kidnapping, or immediate danger",
    ),
    (
        r"(एक्सीडेंट|दुर्घटना|अस्पताल|आईसीयू|ऑपरेशन|बचा\s*लो|मदद\s*करो|खतरे\s*में)",
        ScamCategory.DISTRESS,
        2,
        "Devanagari: Accident, hospital, emergency plea",
    ),

    # 5. URGENCY & TIMEOUT PRESSURE (Do it right now)
    (
        r"\b(immediately|right\s*now|within\s*\d+\s*minutes?|hurry\s*up|fast|quick|turant|jaldi|abhi\s*ke\s*abhi|der\s*mat\s*karo|fatafat)\b",
        ScamCategory.URGENCY,
        2,
        "Temporal coercion demanding instantaneous action",
    ),
    (
        r"(तुरंत|जल्दी|अभी\s*के\s*अभी|देर\s*मत\s*करो|फटाफट)",
        ScamCategory.URGENCY,
        2,
        "Devanagari: Immediately, right now, hurry up",
    ),

    # 6. DEVICE / CALL EXCUSE (Unrecognized caller justification)
    (
        r"\b(new\s*number|friend'?s\s*phone|lost\s*my\s*phone|phone\s*(kharab|damage|chori|stolen)|dost\s*ka\s*phone|naya\s*number|dusre\s*number\s*se)\b",
        ScamCategory.DEVICE_EXCUSE,
        2,
        "Explaining unfamiliar caller ID or number",
    ),
    (
        r"(नया\s*नंबर|दोस्त\s*का\s*फोन|फोन\s*खराब|फोन\s*चोरी|दूसरे\s*नंबर)",
        ScamCategory.DEVICE_EXCUSE,
        2,
        "Devanagari: New number or friend's phone excuse",
    ),
]


class ScamLexicon:
    """Compiled multilingual lexicon matcher."""

    def __init__(self, patterns: List[Tuple[str, ScamCategory, int, str]] | None = None) -> None:
        raw = patterns or RAW_PATTERNS
        self.entries: List[LexiconEntry] = [
            LexiconEntry(pattern=p, category=cat, weight=w, description=desc)
            for p, cat, w, desc in raw
        ]

    def match(self, text: str) -> List[Tuple[LexiconEntry, str]]:
        """Finds all matching pattern entries within the given transcript text.
        
        Returns:
            List of (LexiconEntry, matched_substring) tuples.
        """
        if not text:
            return []

        results: List[Tuple[LexiconEntry, str]] = []
        for entry in self.entries:
            match = entry.compiled.search(text)
            if match:
                results.append((entry, match.group(0)))
        return results

    def extract_categories(self, text: str) -> Dict[ScamCategory, List[str]]:
        """Extracts matched triggers grouped by ScamCategory."""
        matches = self.match(text)
        grouped: Dict[ScamCategory, List[str]] = {}
        for entry, matched_sub in matches:
            grouped.setdefault(entry.category, []).append(matched_sub)
        return grouped
