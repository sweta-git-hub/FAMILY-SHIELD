"""
Family Voice Shield (FVS) - Elderly UX & Accessibility Engine
Provides:
- Bilingual voice prompt catalog (English & Hindi)
- Senior-focused accessibility presets (large font, high contrast)
- Safe emergency actions (Hang up & call back, Family SOS alert)
- Risk-free Practice Call simulator ("अभ्यास कॉल मोड")
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple


class Language(str, Enum):
    EN = "en"
    HI = "hi"


class PromptKey(str, Enum):
    ASK_FOR_CODE = "ASK_FOR_CODE"
    CALLER_VERIFIED = "CALLER_VERIFIED"
    WRONG_CODE_WARNING = "WRONG_CODE_WARNING"
    LOCKOUT_FRAUD_ALERT = "LOCKOUT_FRAUD_ALERT"
    DURESS_TRIGGERED = "DURESS_TRIGGERED"
    PRACTICE_WELCOME = "PRACTICE_WELCOME"
    PRACTICE_SUCCESS = "PRACTICE_SUCCESS"
    PRACTICE_INSTRUCTION = "PRACTICE_INSTRUCTION"


VOICE_PROMPT_CATALOG: Dict[Language, Dict[PromptKey, str]] = {
    Language.EN: {
        PromptKey.ASK_FOR_CODE: "Please ask the caller to read their 6-digit family safety code.",
        PromptKey.CALLER_VERIFIED: "Identity verified! This is your genuine family member. It is safe to talk.",
        PromptKey.WRONG_CODE_WARNING: "Warning: Wrong code entered. Please ask them to repeat the digits carefully.",
        PromptKey.LOCKOUT_FRAUD_ALERT: (
            "Emergency Alert! Suspected AI Voice Clone attack. Do not send money. "
            "Hang up immediately and call your child directly."
        ),
        PromptKey.DURESS_TRIGGERED: "Emergency duress alert active. Stay calm, do not confront the caller.",
        PromptKey.PRACTICE_WELCOME: (
            "Welcome to Practice Call mode. This is a safe training session to practice "
            "asking for and verifying the code."
        ),
        PromptKey.PRACTICE_SUCCESS: "Great job! You successfully verified the family code. You are ready.",
        PromptKey.PRACTICE_INSTRUCTION: (
            "Pretend your child Rahul is calling. Ask him for his code, then type it into the big keypad."
        ),
    },
    Language.HI: {
        PromptKey.ASK_FOR_CODE: "कृपया फोन करने वाले से उनका ६-अंकों का फैमिली कोड पूछें।",
        PromptKey.CALLER_VERIFIED: "पहचान सत्यापित हो गई है! यह आपके असली परिजन हैं। बात करना सुरक्षित है।",
        PromptKey.WRONG_CODE_WARNING: "चेतावनी: गलत कोड दर्ज किया गया। कृपया ध्यान से दोबारा पूछें।",
        PromptKey.LOCKOUT_FRAUD_ALERT: (
            "सावधान! फर्जी आवाज से ठगी का खतरा! पैसे बिल्कुल न भेजें। "
            "तुरंत फोन काटें और सीधे अपने बच्चे को फोन लगाएं।"
        ),
        PromptKey.DURESS_TRIGGERED: "आपातकालीन संकट चेतावनी! शांत रहें और कॉलर से बहस न करें।",
        PromptKey.PRACTICE_WELCOME: (
            "अभ्यास कॉल मोड में आपका स्वागत है। यहाँ आप बिना किसी डर के "
            "कोड पूछने और जांचने का अभ्यास कर सकते हैं।"
        ),
        PromptKey.PRACTICE_SUCCESS: "बहुत बढ़िया! आपने कोड का सही मिलान किया। आप सुरक्षित रहने के लिए तैयार हैं।",
        PromptKey.PRACTICE_INSTRUCTION: (
            "मान लीजिए आपका बेटा राहुल फोन पर है। उससे कोड पूछें और बड़े बटन वाले कीपैड पर दर्ज करें।"
        ),
    },
}


@dataclass
class AccessibilityConfig:
    """Settings tailored for seniors and low-vision users."""
    large_font: bool = True
    high_contrast: bool = False
    voice_prompts_enabled: bool = True
    haptic_feedback: bool = True
    language: Language = Language.EN


class ElderlySessionManager:
    """Manages accessibility settings, localized spoken prompts, and emergency actions."""

    def __init__(self, config: Optional[AccessibilityConfig] = None):
        self.config = config or AccessibilityConfig()

    def set_language(self, lang: Language) -> None:
        self.config.language = lang

    def toggle_high_contrast(self) -> bool:
        self.config.high_contrast = not self.config.high_contrast
        return self.config.high_contrast

    def get_prompt(self, key: PromptKey, lang: Optional[Language] = None) -> str:
        selected_lang = lang or self.config.language
        catalog = VOICE_PROMPT_CATALOG.get(selected_lang, VOICE_PROMPT_CATALOG[Language.EN])
        return catalog.get(key, VOICE_PROMPT_CATALOG[Language.EN][key])

    def get_emergency_callback_action(self, peer_phone: str, peer_name: str) -> dict:
        """
        Creates direct phone dial instruction to break virtual kidnapping attacks.
        Forces parent to hang up on scammer and dial their child's authentic saved number.
        """
        advice = (
            f"Hang up immediately on the incoming caller! Then tap Call {peer_name} "
            f"below to dial their authentic saved number ({peer_phone}) directly."
        )
        return {
            "action": "HANG_UP_AND_CALL_BACK",
            "dial_uri": f"tel:{peer_phone}",
            "contact_name": peer_name,
            "phone_number": peer_phone,
            "instruction": advice,
        }

    def broadcast_family_sos(
        self,
        guardian_phone: str,
        suspect_phone: str,
        peer_name: str,
        reason: str = "3_FAILED_CODE_ATTEMPTS",
    ) -> dict:
        """
        Generates simulated emergency notification for all paired family guardians (MOCK).
        """
        return {
            "status": "SOS_BROADCAST_SENT",
            "mock": True,
            "guardian_phone": guardian_phone,
            "suspect_caller": suspect_phone,
            "targeted_member": peer_name,
            "reason": reason,
            "message": (
                f"[FAMILY SHIELD ALERT] Suspected voice clone fraud call targeting {guardian_phone} "
                f"impersonating {peer_name}. Call attempts failed verification. All family members alerted."
            ),
        }


class PracticeCallSession:
    """
    Stress-free training simulator for elderly guardians.
    Completely isolated from production lockout counters.
    """

    MOCK_SCENARIOS = {
        "legitimate_child": {
            "caller_name": "Rahul (Son - Practice)",
            "scenario_text": "Mom, I am just checking in from hostel. Here is my practice safety code:",
            "mock_code": "842109",
            "is_real_child": True,
        },
        "scammer_attack": {
            "caller_name": "Unknown Number (Voice Clone - Practice)",
            "scenario_text": "Mom! I need urgent money! Don't ask questions! (Refuses to give valid code)",
            "mock_code": "999999",
            "is_real_child": False,
        },
    }

    def __init__(self, scenario_key: str = "legitimate_child"):
        self.scenario_key = scenario_key
        self.scenario = self.MOCK_SCENARIOS.get(
            scenario_key, self.MOCK_SCENARIOS["legitimate_child"]
        )
        self.attempts = 0
        self.completed = False

    def get_prompt_text(self, lang: Language = Language.EN) -> Tuple[str, str]:
        """Returns (headline, instructions) for the practice scenario."""
        if lang == Language.HI:
            head = f"अभ्यास कॉल: {self.scenario['caller_name']}"
            desc = f"{self.scenario['scenario_text']} कोड: {self.scenario['mock_code']}"
        else:
            head = f"Practice Call: {self.scenario['caller_name']}"
            desc = f"{self.scenario['scenario_text']} Code: {self.scenario['mock_code']}"
        return head, desc

    def evaluate_code(self, candidate_code: str) -> dict:
        """Evaluates practice attempt without affecting any live account lockout."""
        self.attempts += 1
        cleaned = candidate_code.strip()

        if cleaned == self.scenario["mock_code"]:
            self.completed = True
            return {
                "success": True,
                "message": "Perfect! You successfully verified the practice code.",
                "attempts": self.attempts,
            }
        else:
            return {
                "success": False,
                "message": (
                    f"Not quite right. The practice code was {self.scenario['mock_code']}. "
                    "Try typing it again on the keypad."
                ),
                "attempts": self.attempts,
            }
