"""
Unit tests for Elderly UX, Bilingual Spoken Prompts, and Practice Call Mode.
"""

import unittest

from core.elderly_ux import (
    AccessibilityConfig,
    ElderlySessionManager,
    Language,
    PracticeCallSession,
    PromptKey,
    VOICE_PROMPT_CATALOG,
)


class TestElderlyUX(unittest.TestCase):
    def setUp(self):
        self.manager = ElderlySessionManager()

    def test_voice_prompt_catalog_completeness(self):
        # Ensure all prompt keys exist and are non-empty in both EN and HI
        for lang in [Language.EN, Language.HI]:
            for key in PromptKey:
                prompt = self.manager.get_prompt(key, lang=lang)
                self.assertIsInstance(prompt, str)
                self.assertTrue(len(prompt) > 10, f"Prompt {key} in {lang} is too short or missing")

    def test_language_switching(self):
        self.manager.set_language(Language.EN)
        prompt_en = self.manager.get_prompt(PromptKey.CALLER_VERIFIED)
        self.assertIn("Identity verified", prompt_en)

        self.manager.set_language(Language.HI)
        prompt_hi = self.manager.get_prompt(PromptKey.CALLER_VERIFIED)
        self.assertIn("पहचान सत्यापित", prompt_hi)

    def test_high_contrast_toggle(self):
        self.assertFalse(self.manager.config.high_contrast)
        enabled = self.manager.toggle_high_contrast()
        self.assertTrue(enabled)
        self.assertTrue(self.manager.config.high_contrast)
        disabled = self.manager.toggle_high_contrast()
        self.assertFalse(disabled)

    def test_emergency_callback_action(self):
        action = self.manager.get_emergency_callback_action(
            peer_phone="+919876543210", peer_name="Rahul"
        )
        self.assertEqual(action["action"], "HANG_UP_AND_CALL_BACK")
        self.assertEqual(action["dial_uri"], "tel:+919876543210")
        self.assertIn("Hang up immediately", action["instruction"])

    def test_family_sos_broadcast_is_mocked(self):
        sos = self.manager.broadcast_family_sos(
            guardian_phone="+919876500001",
            suspect_phone="+919999999999",
            peer_name="Rahul",
        )
        self.assertEqual(sos["status"], "SOS_BROADCAST_SENT")
        self.assertTrue(sos["mock"])
        self.assertIn("Rahul", sos["message"])

    def test_practice_call_session_legitimate(self):
        practice = PracticeCallSession(scenario_key="legitimate_child")
        head, desc = practice.get_prompt_text(lang=Language.EN)
        self.assertIn("Practice Call", head)
        self.assertIn("842109", desc)

        # Wrong attempt
        res_fail = practice.evaluate_code("111111")
        self.assertFalse(res_fail["success"])
        self.assertEqual(practice.attempts, 1)

        # Correct attempt
        res_ok = practice.evaluate_code("842109")
        self.assertTrue(res_ok["success"])
        self.assertTrue(practice.completed)
        self.assertEqual(practice.attempts, 2)

    def test_practice_call_session_hindi(self):
        practice = PracticeCallSession(scenario_key="legitimate_child")
        head, desc = practice.get_prompt_text(lang=Language.HI)
        self.assertIn("अभ्यास कॉल", head)
        self.assertIn("842109", desc)


if __name__ == "__main__":
    unittest.main()
