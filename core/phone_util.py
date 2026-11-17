"""
Family Voice Shield (FVS) - Phone & Contact Utility
Handles E.164 phone normalization, validation, and contact profile schema.
"""

import re
from dataclasses import dataclass
from typing import Optional


# E.164 standard: + followed by 7 to 15 decimal digits
_E164_REGEX = re.compile(r"^\+[1-9]\d{6,14}$")


def normalize_phone_number(raw_phone: str, default_country_code: str = "+91") -> str:
    """
    Normalizes arbitrary phone number inputs into strict E.164 format.
    - Strips whitespace, hyphens, parentheses, and dots.
    - Converts 00-prefix international notation to '+'.
    - If no international prefix is present:
      - Strips leading zero (e.g., Indian STD '09876543210' -> '+919876543210').
      - Prepends the default country code (+91 by default).
    - Validates against ITU E.164: 7 to 15 digits with leading '+'.
    """
    if not raw_phone or not isinstance(raw_phone, str):
        raise ValueError("Phone number must be a non-empty string")

    cleaned = raw_phone.strip()

    # Replace leading international dialling prefix 00 with +
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]

    # Strip characters commonly found in formatted numbers: space, dash, dots, parentheses
    digits_only = re.sub(r"[^\d+]", "", cleaned)

    if not digits_only or digits_only == "+":
        raise ValueError(f"Invalid phone number contains no digits: '{raw_phone}'")

    if digits_only.startswith("+"):
        normalized = digits_only
    else:
        # Domestic format handling
        if digits_only.startswith("0"):
            digits_only = digits_only[1:]
        default_code = default_country_code.strip()
        if not default_code.startswith("+"):
            default_code = "+" + default_code
        normalized = f"{default_code}{digits_only}"

    if not _E164_REGEX.match(normalized):
        raise ValueError(
            f"Phone number '{raw_phone}' does not conform to ITU-T E.164 standard (result: '{normalized}')"
        )

    return normalized


def format_phone_display(phone_e164: str) -> str:
    """
    Formats an E.164 phone number for readable display in UI.
    Example: '+919876543210' -> '+91 98765 43210'
             '+15551234567' -> '+1 (555) 123-4567'
    """
    if not phone_e164.startswith("+"):
        return phone_e164

    # Common formatting for 10-digit national numbers (+91 India)
    if phone_e164.startswith("+91") and len(phone_e164) == 13:
        return f"+91 {phone_e164[3:8]} {phone_e164[8:13]}"
    # US/Canada (+1)
    if phone_e164.startswith("+1") and len(phone_e164) == 12:
        return f"+1 ({phone_e164[2:5]}) {phone_e164[5:8]}-{phone_e164[8:12]}"

    return phone_e164


@dataclass(frozen=True)
class ContactProfile:
    """Metadata representing a family member in the contacts list."""
    phone: str  # E.164 format
    name: str
    relationship: str = "Family Member"
    notes: Optional[str] = None

    def __post_init__(self):
        # Validate E.164 on construction
        if not _E164_REGEX.match(self.phone):
            raise ValueError(f"Invalid E.164 phone: '{self.phone}'")
        if not self.name or not self.name.strip():
            raise ValueError("Contact name cannot be empty")
