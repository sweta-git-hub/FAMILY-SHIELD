"""Comprehensive adversarial red-team test suite for Family Voice Shield.

Evaluates system resilience against:
1. Semantic scam lexicon evasion (polite framing, code-mixing, dilution attacks).
2. Acoustic synthetic voice evasion under G.711 carrier telephony degradation.
3. Multimodal fusion override attacks (benign speech cloaking voice clone, natural voice cloaking extortion).
4. Cryptographic replay, directional key inversion, and brute-force lockout defenses.
5. Covert duress signaling and emergency safety actions.
"""

from __future__ import annotations

import math
import struct
import unittest

from core.alert_tiers import AlertStateMachine, AlertTier
from core.crypto import (
    derive_directional_keys,
    derive_duress_key,
    totp,
    verify_numeric,
    LockoutSession,
    VerificationResult,
)
from core.elderly_ux import ElderlySessionManager
from ml.antispoof_engine import AcousticArtifactDetector, AcousticFeatureExtractor
from ml.fusion import MultimodalFusionEngine
from ml.scam_classifier import NoisyOrScamClassifier
from ml.scam_lexicon import ScamCategory, ScamLexicon
from ml.telephony_codec import TelephonyCodecSimulator


def _make_pcm_tone(freq_hz: float, duration_sec: float = 3.0, sample_rate: int = 16000, amplitude: float = 0.5) -> bytes:
    """Generates synthetic pure-tone PCM audio (simulating flat synthetic tone)."""
    total_samples = int(sample_rate * duration_sec)
    buf = bytearray(total_samples * 2)
    for i in range(total_samples):
        val = int(amplitude * 32767.0 * math.sin(2.0 * math.pi * freq_hz * i / sample_rate))
        val = max(-32768, min(32767, val))
        struct.pack_into("<h", buf, i * 2, val)
    return bytes(buf)


def _make_dynamic_pcm(duration_sec: float = 3.0, sample_rate: int = 16000) -> bytes:
    """Generates dynamic multi-harmonic audio with pitch variation (simulating natural speech)."""
    total_samples = int(sample_rate * duration_sec)
    buf = bytearray(total_samples * 2)
    for i in range(total_samples):
        t = i / sample_rate
        f0 = 140.0 + 40.0 * math.sin(2.0 * math.pi * 1.5 * t)
        val = 0.3 * math.sin(2.0 * math.pi * f0 * t) + 0.15 * math.sin(2.0 * math.pi * 2.0 * f0 * t)
        if (i // 1600) % 3 == 0:
            val += 0.08 * (math.sin(2.0 * math.pi * 3200.0 * t))
        int_val = int(val * 32767.0)
        int_val = max(-32768, min(32767, int_val))
        struct.pack_into("<h", buf, i * 2, int_val)
    return bytes(buf)


class TestSemanticRedTeamEvasion(unittest.TestCase):
    """Red-team tests for semantic scam detection evasion."""

    def setUp(self) -> None:
        self.lexicon = ScamLexicon()
        self.classifier = NoisyOrScamClassifier(lexicon=self.lexicon)

    def test_all_six_categories_detected_across_languages(self) -> None:
        """Verify adversarial triggers in all 6 categories across English, Hindi, and Hinglish."""
        test_phrases = {
            ScamCategory.AUTHORITY: [
                "You are under digital arrest by CBI officer",
                "थाने से बोल रहा हूँ पुलिस केस दर्ज हुआ है",
                "arrest warrant issued against your aadhaar card",
            ],
            ScamCategory.SECRECY: [
                "Don't tell anyone about this call, stay on the line",
                "kisi ko mat batana phone mat kaatna",
                "लाइन पर रहो और किसी से बात मत करो",
            ],
            ScamCategory.FINANCIAL: [
                "Send the clearance amount via UPI immediately",
                "तुरंत पैसे भेजो और खाते में डालो",
                "Approve the transfer request on PhonePe or GPay right now",
            ],
            ScamCategory.DISTRESS: [
                "Your son met with a severe accident and is in hospital ICU",
                "मम्मी मुझे बचा लो बहुत बड़ी मुसीबत में हूँ",
                "arrested in criminal matter, need bail money urgently",
            ],
            ScamCategory.URGENCY: [
                "Action must be taken immediately right now",
                "turant jaldi karo abhi ke abhi",
                "तुरंत फटाफट जवाब दो समय नहीं है",
            ],
            ScamCategory.DEVICE_EXCUSE: [
                "Calling from a friend's phone because my phone broke",
                "naya number hai purana phone kharab ho gaya",
                "दोस्त का नया नंबर है मेरा फोन बंद हो गया",
            ],
        }

        for category, phrases in test_phrases.items():
            for phrase in phrases:
                detected = self.lexicon.extract_categories(phrase)
                self.assertIn(
                    category,
                    detected,
                    f"Category '{category.value}' failed detection on phrase: '{phrase}'",
                )

    def test_compound_scam_adversarial_escalation(self) -> None:
        """Verify that compound multi-tactic extortion escalates to RED tier."""
        extortion_text = (
            "Hello, this is CBI digital arrest department. Your son is in our police custody "
            "after a terrible hospital accident. Kisi ko mat batana, turant UPI transfer the "
            "bail money right now, do not disconnect the line."
        )
        res = self.classifier.classify_text(extortion_text)
        self.assertGreaterEqual(res.s_t, 0.70)
        self.assertTrue(res.is_critical)
        self.assertIn(ScamCategory.AUTHORITY, res.matched_categories)
        self.assertIn(ScamCategory.FINANCIAL, res.matched_categories)
        self.assertIn(ScamCategory.SECRECY, res.matched_categories)

    def test_dilution_attack_resistance(self) -> None:
        """Adversary surrounds scam demand with 100+ words of harmless casual conversation."""
        benign_prefix = "Good morning! The weather here in Delhi is really pleasant today. I went to the vegetable market " \
                        "and bought fresh coriander and ginger. How is uncle doing? Hope his knee pain has reduced. "
        scam_core = "By the way, digital arrest warrant has been issued so please transfer money on UPI immediately. "
        benign_suffix = "Anyway, call me back when you get time. We should all meet next Sunday for lunch."

        diluted_text = benign_prefix + scam_core + benign_suffix
        res = self.classifier.classify_text(diluted_text)

        # Dilution must NOT hide the authority and financial coercion
        self.assertGreaterEqual(res.s_t, 0.70, "Dilution attack successfully suppressed scam score!")
        self.assertTrue(res.is_critical)

    def test_benign_casual_conversation_stays_safe(self) -> None:
        """Natural benign conversation with incidental words must remain in GREEN tier."""
        benign_samples = [
            "Mummy, train late ho gayi hai. Main shaam tak ghar pahunch jaunga.",
            "I checked the doctor appointment for tomorrow morning at 10 AM.",
            "Can you send the recipe for that paneer sabzi you made last week?",
            "Papa called earlier, he said everything is fine at the office.",
        ]
        for sample in benign_samples:
            res = self.classifier.classify_text(sample)
            self.assertLess(
                res.s_t,
                0.20,
                f"Benign text triggered false alarm: '{sample}' (score={res.s_t})",
            )


class TestAcousticAndTelephonyRedTeam(unittest.TestCase):
    """Red-team tests for acoustic synthetic voice and telephony channel effects."""

    def setUp(self) -> None:
        self.codec = TelephonyCodecSimulator()
        self.detector = AcousticArtifactDetector()
        self.extractor = AcousticFeatureExtractor()

    def test_carrier_telephony_codec_degradation_preserves_detector(self) -> None:
        """Verify G.711 mu-law, 8kHz downsampling, and 300-3400Hz filter on synthetic audio."""
        raw_synthetic = _make_pcm_tone(220.0, duration_sec=3.0, sample_rate=16000)

        # Run through aggressive G.711 carrier telephony degradation
        degraded_telephony = self.codec.simulate_telephony_channel(
            raw_synthetic,
            codec="g711_ulaw",
            apply_bandpass=True,
            simulate_loss=True,
            packet_loss_rate=0.03,
        )

        res = self.detector.score_audio(degraded_telephony, sample_rate=16000)
        # Synthetic flat tone must remain detectable even through degraded telephony
        self.assertGreaterEqual(res.s_a, 0.70, "Carrier degradation masked synthetic audio artifact!")

    def test_natural_speech_telephony_no_false_positive(self) -> None:
        """Dynamic natural speech passed through carrier telephony must not trigger false positive."""
        natural_audio = _make_dynamic_pcm(duration_sec=3.0, sample_rate=16000)
        degraded = self.codec.simulate_telephony_channel(
            natural_audio,
            codec="g711_ulaw",
            apply_bandpass=True,
            simulate_loss=False,
        )

        res = self.detector.score_audio(degraded, sample_rate=16000)
        self.assertLess(
            res.s_a,
            0.40,
            f"Natural speech falsely flagged as synthetic deepfake (score={res.s_a})",
        )

    def test_spliced_audio_adversarial_attack(self) -> None:
        """Adversary splices 1 second of natural audio with 2 seconds of vocoder tone."""
        part_natural = _make_dynamic_pcm(duration_sec=1.0, sample_rate=16000)
        part_synthetic = _make_pcm_tone(300.0, duration_sec=2.0, sample_rate=16000)
        spliced_pcm = part_natural + part_synthetic

        res = self.detector.score_audio(spliced_pcm, sample_rate=16000)
        # The 2.0s synthetic section must trigger elevated acoustic suspicion
        self.assertGreaterEqual(res.s_a, 0.50, "Spliced synthetic voice went undetected!")


class TestMultimodalFusionOverrideStress(unittest.TestCase):
    """Red-team tests for multimodal logistic fusion override guarantees."""

    def setUp(self) -> None:
        self.fusion = MultimodalFusionEngine()
        self.state_machine = AlertStateMachine()

    def test_benign_text_cloak_cannot_suppress_synthetic_voice(self) -> None:
        """Critical deepfake voice clone (s_a=0.85) reading completely benign text (s_t=0.02).

        The fail-safe override MUST guarantee an immediate RED alert.
        """
        result = self.fusion.fuse(s_a=0.85, s_t=0.02, s_c=0.05)
        self.assertGreaterEqual(result.fused_risk, 0.70, "Benign text suppressed synthetic voice alert!")
        self.assertTrue(result.is_critical_override)
        self.assertEqual(result.dominant_modality, "acoustic")

        tier, _ = self.state_machine.update(result.fused_risk)
        self.assertEqual(tier, AlertTier.RED)

    def test_natural_acoustic_cloak_cannot_suppress_scam_extortion(self) -> None:
        """Natural human voice (s_a=0.05) conducting high-threat digital arrest scam (s_t=0.92).

        The fail-safe override MUST guarantee an immediate RED alert.
        """
        result = self.fusion.fuse(s_a=0.05, s_t=0.92, s_c=0.05)
        self.assertGreaterEqual(result.fused_risk, 0.70, "Natural voice suppressed scam language alert!")
        self.assertTrue(result.is_critical_override)
        self.assertEqual(result.dominant_modality, "semantic")

        tier, _ = self.state_machine.update(result.fused_risk)
        self.assertEqual(tier, AlertTier.RED)

    def test_compounding_borderline_indicators_escalate_to_amber_or_red(self) -> None:
        """Elevated acoustic (s_a=0.62) + elevated semantic (s_t=0.62) + context (s_c=0.35).

        Together they compound to high threat.
        """
        result = self.fusion.fuse(s_a=0.62, s_t=0.62, s_c=0.35)
        self.assertGreaterEqual(result.fused_risk, 0.55)

        tier, _ = self.state_machine.update(result.fused_risk)
        self.assertIn(tier, [AlertTier.AMBER, AlertTier.RED])


class TestCryptographicRedTeamDefense(unittest.TestCase):
    """Red-team tests for cryptographic replay, directional isolation, and brute force."""

    def test_directional_key_swap_attack(self) -> None:
        """Adversary intercepts code shown on Guardian device and attempts to replay it to Member.

        Directional derivation (FVS1|A->B != FVS1|B->A) must reject the code.
        """
        k_pair = b"01234567890123456789"  # 160-bit pairing secret
        k_a_to_b, k_b_to_a = derive_directional_keys(k_pair)
        self.assertNotEqual(k_a_to_b, k_b_to_a)

        timestamp = 1700000000
        # Code generated for A -> B
        code_a_to_b = totp(k_a_to_b, timestamp=timestamp, step=60)

        # Attacker tries to verify this code as B -> A
        is_valid_reverse = verify_numeric(k_b_to_a, code_a_to_b, timestamp=timestamp, step=60)
        self.assertFalse(is_valid_reverse, "Directional attack succeeded! A->B code accepted as B->A!")

    def test_stale_replay_attack_outside_window(self) -> None:
        """Code intercepted 180 seconds ago must fail verification."""
        key = b"secret_key_1234567890"
        t_original = 1700000000
        t_replayed = t_original + 180  # 3 minutes (3 steps) later

        code = totp(key, timestamp=t_original, step=60)
        valid = verify_numeric(key, code, timestamp=t_replayed, step=60, window=1)
        self.assertFalse(valid, "Stale replay attack succeeded outside allowable skew window!")

    def test_brute_force_lockout_state_machine(self) -> None:
        """Attacker sends 3 consecutive incorrect codes -> system enters LOCKED state."""
        key = b"safe_vault_key_12345"
        timestamp = 1700000000
        real_code = totp(key, timestamp=timestamp, step=60)

        session = LockoutSession(key_dir=key, max_attempts=3)
        bad_codes = ["000000", "111111", "222222"]

        for i, bad_code in enumerate(bad_codes):
            res = session.check_numeric(bad_code, timestamp=timestamp, step=60)
            if i < 2:
                self.assertEqual(res, VerificationResult.INVALID)
                self.assertFalse(session.is_locked)
            else:
                self.assertEqual(res, VerificationResult.LOCKED_OUT)
                self.assertTrue(session.is_locked, "System failed to lock after 3 failed attempts!")

        # Even if attacker now submits the TRUE code, locked state must reject it
        res_post_lock = session.check_numeric(real_code, timestamp=timestamp, step=60)
        self.assertEqual(res_post_lock, VerificationResult.LOCKED_OUT, "Locked system allowed valid code!")
        self.assertTrue(session.is_locked)


class TestDuressAndSafetyActions(unittest.TestCase):
    """Red-team tests for duress detection and emergency callback generation."""

    def test_duress_trigger_creates_emergency_alert(self) -> None:
        """Coerced victim enters secret duress code or triggers SOS."""
        manager = ElderlySessionManager()
        sos = manager.broadcast_family_sos(
            guardian_phone="+919876543210",
            suspect_phone="+911122334455",
            peer_name="Rahul",
            reason="Suspected digital arrest / coercion",
        )
        self.assertEqual(sos["status"], "SOS_BROADCAST_SENT")
        self.assertEqual(sos["guardian_phone"], "+919876543210")
        self.assertIn("digital arrest", sos["reason"])

    def test_emergency_callback_uri_formatting(self) -> None:
        """Verify 'Hang Up & Call Back' link dials true saved E.164 number."""
        manager = ElderlySessionManager()
        action = manager.get_emergency_callback_action(
            peer_phone="+919876543210",
            peer_name="Rahul",
        )
        self.assertEqual(action["action"], "HANG_UP_AND_CALL_BACK")
        self.assertEqual(action["dial_uri"], "tel:+919876543210")
        self.assertEqual(action["phone_number"], "+919876543210")


if __name__ == "__main__":
    unittest.main()
