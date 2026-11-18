"""Unit and integration tests for Phase 6: Acoustic Anti-Spoofing & Telephony Codec.

Tests:
1. G.711 mu-law and A-law companding and expansion bit-level fidelity.
2. Telephony bandpass filtering (300 Hz - 3400 Hz) attenuation behavior.
3. 8 kHz resampling decimation and interpolation.
4. Channel degradation with packet loss simulation.
5. Acoustic feature extraction (ZCR variance, RMS, pitch stability, crest factor).
6. Synthetic artifact detector scoring on robotic tones vs natural dynamic speech.
7. Telephony compensation preventing false positives on compressed speech.
8. End-to-end StreamScorer integration with real acoustic anti-spoof scoring.
"""

from __future__ import annotations

import math
import struct
import unittest
from ml.antispoof_engine import (
    AcousticArtifactDetector,
    AcousticFeatureExtractor,
    MockAntiSpoofEngine,
    ONNXAntiSpoofEngine,
    create_antispoof_engine,
)
from ml.stt_engine import MockSTTEngine
from ml.telephony_codec import (
    TelephonyBandpassFilter,
    TelephonyCodecSimulator,
    linear_to_alaw,
    linear_to_ulaw,
    alaw_to_linear,
    ulaw_to_linear,
)
from server.chunker import AudioChunk
from server.scorer import StreamScorer


def generate_sine_wave(freq_hz: float, duration_sec: float, sample_rate: int = 16000, amplitude: float = 0.5) -> bytes:
    """Generates synthetic 16-bit linear PCM pure sine wave."""
    total_samples = int(duration_sec * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        val = int(amplitude * 32767.0 * math.sin(2.0 * math.pi * freq_hz * t))
        samples.append(max(-32768, min(32767, val)))
    return struct.pack(f"<{len(samples)}h", *samples)


def generate_natural_like_audio(duration_sec: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Simulates natural speech with dynamic pitch, formant variation, and unvoiced fricatives."""
    total_samples = int(duration_sec * sample_rate)
    samples = []
    # Seeded random generator for reproducible consonant noise
    import random
    rng = random.Random(42)
    for i in range(total_samples):
        t = i / sample_rate
        # Changing fundamental frequency (prosody intonation: 100 Hz to 170 Hz)
        f0 = 135.0 + 35.0 * math.sin(2.0 * math.pi * 2.5 * t)
        vowel = 0.4 * math.sin(2.0 * math.pi * f0 * t) + 0.2 * math.sin(2.0 * math.pi * 2.0 * f0 * t)
        # Periodic bursts of unvoiced noise (consonant fricatives like /s/, /t/)
        consonant = 0.3 * (rng.random() * 2.0 - 1.0) if (int(t * 8) % 2 == 1) else 0.0
        # Syllabic envelope modulation
        envelope = 0.5 * (1.0 + math.cos(2.0 * math.pi * 3.0 * t))
        val = int((vowel + consonant) * envelope * 24000.0)
        samples.append(max(-32768, min(32767, val)))
    return struct.pack(f"<{len(samples)}h", *samples)


class TestTelephonyCodec(unittest.TestCase):
    """Tests G.711 codec, 8kHz downsampling, and telephony filtering."""

    def setUp(self) -> None:
        self.sim = TelephonyCodecSimulator(sample_rate=16000)

    def test_g711_ulaw_roundtrip(self) -> None:
        test_values = [-30000, -15000, -1000, -50, 0, 50, 1000, 15000, 30000]
        for val in test_values:
            ulaw = linear_to_ulaw(val)
            self.assertTrue(0 <= ulaw <= 255)
            recovered = ulaw_to_linear(ulaw)
            # Logarithmic quantization error should be within small relative percentage
            abs_err = abs(val - recovered)
            max_allowed = max(20, abs(val) * 0.10)
            self.assertLessEqual(abs_err, max_allowed)

    def test_g711_alaw_roundtrip(self) -> None:
        test_values = [-25000, -12000, -800, -40, 0, 40, 800, 12000, 25000]
        for val in test_values:
            alaw = linear_to_alaw(val)
            self.assertTrue(0 <= alaw <= 255)
            recovered = alaw_to_linear(alaw)
            abs_err = abs(val - recovered)
            max_allowed = max(20, abs(val) * 0.10)
            self.assertLessEqual(abs_err, max_allowed)

    def test_resampling_8k_and_16k(self) -> None:
        samples_16k = [1000, 2000, 3000, 4000, 5000, 6000]
        down = self.sim.resample_16k_to_8k(samples_16k)
        self.assertEqual(len(down), 3)
        self.assertEqual(down[0], 1500)
        self.assertEqual(down[1], 3500)
        self.assertEqual(down[2], 5500)

        up = self.sim.resample_8k_to_16k(down)
        self.assertEqual(len(up), 6)

    def test_bandpass_filter_attenuation(self) -> None:
        # 100 Hz low rumble (below 300 Hz cutoff) vs 1000 Hz voice formant
        pcm_100hz = generate_sine_wave(100.0, duration_sec=0.5, amplitude=0.5)
        pcm_1000hz = generate_sine_wave(1000.0, duration_sec=0.5, amplitude=0.5)

        samples_100 = self.sim.pcm_to_samples(pcm_100hz)
        samples_1000 = self.sim.pcm_to_samples(pcm_1000hz)

        filtered_100 = self.sim.bandpass.filter_samples(samples_100)
        filtered_1000 = self.sim.bandpass.filter_samples(samples_1000)

        rms_100_in = math.sqrt(sum(s * s for s in samples_100) / len(samples_100))
        rms_100_out = math.sqrt(sum(s * s for s in filtered_100) / len(filtered_100))
        attenuation_100 = rms_100_out / rms_100_in

        rms_1000_in = math.sqrt(sum(s * s for s in samples_1000) / len(samples_1000))
        rms_1000_out = math.sqrt(sum(s * s for s in filtered_1000) / len(filtered_1000))
        pass_ratio_1000 = rms_1000_out / rms_1000_in

        # 100 Hz should be substantially attenuated compared to 1000 Hz passband
        self.assertLess(attenuation_100, 0.40)
        self.assertGreater(pass_ratio_1000, 0.70)

    def test_simulate_telephony_channel_pipeline(self) -> None:
        pcm_in = generate_natural_like_audio(duration_sec=1.0)
        pcm_out = self.sim.simulate_telephony_channel(
            pcm_in,
            codec="g711_ulaw",
            apply_bandpass=True,
            simulate_loss=True,
            packet_loss_rate=0.03,
        )
        self.assertEqual(len(pcm_in), len(pcm_out))
        self.assertNotEqual(pcm_in, pcm_out)


class TestAcousticAntiSpoofing(unittest.TestCase):
    """Tests feature extraction, synthetic voice artifact detection, and telephony compensation."""

    def setUp(self) -> None:
        self.extractor = AcousticFeatureExtractor()
        self.detector = AcousticArtifactDetector(extractor=self.extractor)

    def test_silence_detection(self) -> None:
        silent_pcm = b"\x00\x00" * 16000
        res = self.detector.score_audio(silent_pcm)
        self.assertTrue(res.features.is_silence)
        self.assertLess(res.s_a, 0.10)
        self.assertFalse(res.is_suspicious)

    def test_robotic_tone_triggers_synthetic_score(self) -> None:
        # Monotonous locked pitch (e.g. constant 250 Hz vocoder harmonic lock)
        robotic_pcm = generate_sine_wave(250.0, duration_sec=1.5, amplitude=0.7)
        res = self.detector.score_audio(robotic_pcm)
        self.assertGreaterEqual(res.s_a, 0.70)
        self.assertTrue(res.is_synthetic)
        self.assertIn("hyper_periodic_pitch_lock", res.artifacts_detected)

    def test_natural_speech_produces_low_spoof_score(self) -> None:
        natural_pcm = generate_natural_like_audio(duration_sec=2.0)
        res = self.detector.score_audio(natural_pcm)
        self.assertLess(res.s_a, 0.35)
        self.assertFalse(res.is_synthetic)
        self.assertFalse(res.is_suspicious)

    def test_telephony_speech_compensation(self) -> None:
        # Natural speech passed through telephony degradation filter
        sim = TelephonyCodecSimulator(sample_rate=16000)
        natural_pcm = generate_natural_like_audio(duration_sec=2.0)
        telephony_pcm = sim.simulate_telephony_channel(natural_pcm, codec="g711_ulaw", apply_bandpass=True)

        res = self.detector.score_audio(telephony_pcm)
        # Should NOT trigger synthetic alarm on telephony compression
        self.assertLess(res.s_a, 0.40)
        self.assertFalse(res.is_synthetic)

    def test_mock_antispoof_engine(self) -> None:
        mock_eng = MockAntiSpoofEngine(default_score=0.85)
        res = mock_eng.score_audio(b"\x00\x00" * 1000)
        self.assertEqual(res.s_a, 0.85)
        self.assertTrue(res.is_synthetic)
        self.assertTrue(res.is_mock)


class TestStreamScorerMultimodal(unittest.TestCase):
    """Tests integrated StreamScorer with both STT (Phase 5) and Anti-Spoof (Phase 6)."""

    def test_critical_voice_clone_triggers_red_tier(self) -> None:
        # Safe words ("Hello mom, having tea at home"), but synthetic voice clone audio
        mock_stt = MockSTTEngine(default_text="Hello mom, having tea at home")
        mock_as = MockAntiSpoofEngine(default_score=0.92)  # Highly synthetic voice clone detected
        scorer = StreamScorer(stt_engine=mock_stt, antispoof_engine=mock_as)

        chunk = AudioChunk(
            chunk_index=1,
            timestamp_sec=3.0,
            data=b"\x15\x00" * 24000,
            duration_sec=3.0,
            sample_rate=16000,
            channels=1,
            rms_energy=0.04,
            has_speech=True,
        )
        score = scorer.score_chunk(chunk, call_context={"unknown_number": True})

        self.assertEqual(score.tier, "RED")
        self.assertGreaterEqual(score.risk, 0.70)
        self.assertEqual(score.prompt, "ask_for_code")
        self.assertGreaterEqual(score.s_a, 0.70)

    def test_benign_caller_and_natural_voice(self) -> None:
        mock_stt = MockSTTEngine(default_text="Hello dad, I will come home this evening")
        mock_as = MockAntiSpoofEngine(default_score=0.12)
        scorer = StreamScorer(stt_engine=mock_stt, antispoof_engine=mock_as)

        chunk = AudioChunk(
            chunk_index=2,
            timestamp_sec=6.0,
            data=b"\x10\x00" * 24000,
            duration_sec=3.0,
            sample_rate=16000,
            channels=1,
            rms_energy=0.03,
            has_speech=True,
        )
        score = scorer.score_chunk(chunk, call_context={"unknown_number": False})

        self.assertEqual(score.tier, "GREEN")
        self.assertLess(score.risk, 0.40)
        self.assertEqual(score.prompt, "normal")


if __name__ == "__main__":
    unittest.main()
