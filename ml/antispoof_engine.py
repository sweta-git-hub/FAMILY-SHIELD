"""Acoustic Anti-Spoofing & Synthetic Speech Engine for Family Voice Shield.

Detects AI-generated synthetic speech, deepfake voice clones, and vocoder artifacts
on 16 kHz 16-bit linear PCM audio.

Features:
1. Pure-Python acoustic feature extractor (ZCR, pitch stability, RMS dynamics, spectral ratio)
2. Calibrated acoustic artifact detector with telephony channel compensation
3. ONNX Runtime model inference wrapper (AASIST / RawNet / LCNN architecture)
4. Deterministic Mock engine for testing and CI
5. Zero disk persistence (Rule 7)
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple


@dataclass(frozen=True)
class AcousticFeatures:
    """Acoustic characteristics extracted from a 16 kHz linear PCM audio chunk."""
    rms_energy: float                 # Overall RMS energy [0.0 - 1.0]
    zcr_mean: float                   # Mean zero-crossing rate per 20ms frame
    zcr_variance: float               # Variance of ZCR across frames (prosody marker)
    energy_crest_factor: float        # Peak-to-average power ratio (crest factor)
    pitch_stability: float            # Autocorrelation periodicity stability [0.0 - 1.0]
    high_freq_ratio: float            # Ratio of energy in upper spectrum (>3 kHz)
    telephony_signature: bool         # Detected 8 kHz / bandpass G.711 carrier compression
    is_silence: bool                  # Below voice activity threshold


@dataclass(frozen=True)
class AntiSpoofResult:
    """Output of acoustic synthetic speech analysis."""
    s_a: float                        # Calibrated acoustic spoof score [0.0 - 1.0]
    features: AcousticFeatures        # Extracted acoustic metrics
    engine_name: str                  # Engine identifier (ONNX, Algorithmic, Mock)
    is_synthetic: bool                # True if s_a >= 0.70 (RED tier threshold)
    is_suspicious: bool               # True if s_a >= 0.40 (AMBER tier threshold)
    artifacts_detected: List[str]     # Specific synthetic cues detected
    is_mock: bool = False             # Rule 0.5 MOCK indicator


class BaseAntiSpoofEngine(Protocol):
    """Protocol interface for anti-spoofing engines."""
    def score_audio(self, pcm_bytes: bytes, sample_rate: int = 16000) -> AntiSpoofResult:
        ...


class AcousticFeatureExtractor:
    """Extracts temporal and spectral acoustic features from raw 16 kHz linear PCM."""

    def __init__(self, frame_size_ms: float = 20.0, hop_size_ms: float = 10.0) -> None:
        self.frame_size_ms = frame_size_ms
        self.hop_size_ms = hop_size_ms

    def extract(self, pcm_bytes: bytes, sample_rate: int = 16000) -> AcousticFeatures:
        """Analyzes 16-bit PCM bytes and returns AcousticFeatures."""
        count = len(pcm_bytes) // 2
        if count == 0:
            return AcousticFeatures(
                rms_energy=0.0,
                zcr_mean=0.0,
                zcr_variance=0.0,
                energy_crest_factor=1.0,
                pitch_stability=0.0,
                high_freq_ratio=0.0,
                telephony_signature=False,
                is_silence=True,
            )

        samples = struct.unpack(f"<{count}h", pcm_bytes[: count * 2])
        float_samples = [s / 32768.0 for s in samples]

        # 1. Overall RMS Energy & Peak
        sum_sq = sum(s * s for s in float_samples)
        rms = math.sqrt(sum_sq / count)
        peak = max(abs(s) for s in float_samples)
        crest_factor = (peak / rms) if rms > 1e-4 else 1.0

        if rms < 0.010:  # Silence / ambient background noise
            return AcousticFeatures(
                rms_energy=rms,
                zcr_mean=0.0,
                zcr_variance=0.0,
                energy_crest_factor=crest_factor,
                pitch_stability=0.0,
                high_freq_ratio=0.0,
                telephony_signature=False,
                is_silence=True,
            )

        # 2. Frame-level Zero Crossing Rate (ZCR)
        frame_len = int(sample_rate * (self.frame_size_ms / 1000.0))
        hop_len = int(sample_rate * (self.hop_size_ms / 1000.0))
        frame_len = max(frame_len, 10)
        hop_len = max(hop_len, 5)

        zcrs: List[float] = []
        for i in range(0, count - frame_len, hop_len):
            frame = float_samples[i : i + frame_len]
            crossings = 0
            for j in range(len(frame) - 1):
                if (frame[j] >= 0.0 and frame[j + 1] < 0.0) or (frame[j] < 0.0 and frame[j + 1] >= 0.0):
                    crossings += 1
            zcrs.append(crossings / (frame_len - 1))

        if zcrs:
            zcr_mean = sum(zcrs) / len(zcrs)
            zcr_var = sum((z - zcr_mean) ** 2 for z in zcrs) / len(zcrs)
        else:
            zcr_mean = 0.0
            zcr_var = 0.0

        # 3. Autocorrelation Pitch Periodicity & Stability
        # Search lags corresponding to pitch range 80 Hz - 400 Hz
        min_lag = int(sample_rate / 400)  # ~40 samples @ 16kHz
        max_lag = int(sample_rate / 80)   # ~200 samples @ 16kHz
        max_corr = 0.0
        
        # Test autocorrelation on center 1000 samples
        mid = count // 2
        test_window = float_samples[max(0, mid - 500) : min(count, mid + 500)]
        if len(test_window) > max_lag * 2:
            base_power = sum(s * s for s in test_window[:300])
            if base_power > 1e-4:
                for lag in range(min_lag, min(max_lag, len(test_window) - 300), 2):
                    corr = sum(test_window[k] * test_window[k + lag] for k in range(300))
                    normalized_corr = corr / base_power
                    if normalized_corr > max_corr:
                        max_corr = normalized_corr

        pitch_stability = max(0.0, min(1.0, max_corr))

        # 4. High-Frequency Spectral Energy Ratio (First-order difference proxy)
        # Differencing acts as a high-pass pre-emphasis filter
        diff_samples = [float_samples[k] - float_samples[k - 1] for k in range(1, count)]
        diff_energy = sum(d * d for d in diff_samples) / max(1, len(diff_samples))
        hf_ratio = min(2.0, (diff_energy / (rms * rms + 1e-5)))

        # 5. Telephony Signature Detection (absence of natural energy above 3.5 kHz)
        telephony = (hf_ratio < 0.35 and rms > 0.02)

        return AcousticFeatures(
            rms_energy=rms,
            zcr_mean=zcr_mean,
            zcr_variance=zcr_var,
            energy_crest_factor=crest_factor,
            pitch_stability=pitch_stability,
            high_freq_ratio=hf_ratio,
            telephony_signature=telephony,
            is_silence=False,
        )


class AcousticArtifactDetector:
    """Calibrated algorithmic detector for synthetic speech artifacts.
    
    Synthesized/cloned speech commonly shows:
    - Unnaturally constant pitch or abnormal harmonic lock (pitch_stability near 1.0)
    - Exceptionally low ZCR variance (robotic lack of natural phonetic transition dynamics)
    - Abnormally low crest factor (compressed dynamic range typical of neural vocoders)
    - Phase / frame discontinuity glitches
    """

    def __init__(self, extractor: Optional[AcousticFeatureExtractor] = None) -> None:
        self.extractor = extractor or AcousticFeatureExtractor()

    def score_audio(self, pcm_bytes: bytes, sample_rate: int = 16000) -> AntiSpoofResult:
        """Evaluates PCM audio for synthetic speech artifacts."""
        feats = self.extractor.extract(pcm_bytes, sample_rate=sample_rate)

        if feats.is_silence:
            return AntiSpoofResult(
                s_a=0.02,
                features=feats,
                engine_name="AcousticArtifactDetector",
                is_synthetic=False,
                is_suspicious=False,
                artifacts_detected=[],
                is_mock=False,
            )

        artifacts: List[str] = []
        spoof_prob = 0.08  # Baseline false positive rate for natural speech

        # 1. Robotic pitch lock / abnormally high harmonic periodicity
        # Natural human speech pitch naturally fluctuates (jitter/shimmer);
        # TTS / neural vocoders often exhibit hyper-periodic harmonic loops.
        if feats.pitch_stability > 0.94:
            spoof_prob += 0.45
            artifacts.append("hyper_periodic_pitch_lock")
        elif feats.pitch_stability > 0.88:
            spoof_prob += 0.20
            artifacts.append("abnormal_harmonic_regularity")

        # 2. Unnatural ZCR flatness (lack of dynamic phonetic transitions)
        # Human speech exhibits high ZCR variance between vowels and consonants.
        if feats.zcr_variance < 0.0025:
            spoof_prob += 0.35
            artifacts.append("robotic_zcr_flatness")
        elif feats.zcr_variance < 0.0050:
            spoof_prob += 0.15
            artifacts.append("low_phonetic_variance")

        # 3. Dynamic Range / Crest Factor Compression
        # Over-compressed neural vocoder synthesis often reduces natural crest factor.
        if feats.energy_crest_factor < 2.2 and feats.rms_energy > 0.05:
            spoof_prob += 0.20
            artifacts.append("vocoder_dynamic_compression")

        # 4. Telephony Channel Compensation:
        # Carrier G.711 compression reduces high frequencies, but natural human speech
        # retains normal ZCR variance and dynamic range.
        if feats.telephony_signature and "robotic_zcr_flatness" not in artifacts:
            # Dampen spoof probability on genuine carrier telephony speech
            spoof_prob = max(0.05, spoof_prob * 0.75)

        s_a = max(0.0, min(1.0, spoof_prob))

        return AntiSpoofResult(
            s_a=round(s_a, 4),
            features=feats,
            engine_name="AcousticArtifactDetector",
            is_synthetic=(s_a >= 0.70),
            is_suspicious=(s_a >= 0.40),
            artifacts_detected=artifacts,
            is_mock=False,
        )


class ONNXAntiSpoofEngine:
    """Wrapper for ONNX runtime inference (e.g., AASIST or RawNet anti-spoof models)."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        fallback_detector: Optional[AcousticArtifactDetector] = None,
    ) -> None:
        self.model_path = model_path
        self.fallback = fallback_detector or AcousticArtifactDetector()
        self._session = None
        self._available = False

        if model_path:
            try:
                import onnxruntime as ort  # type: ignore
                self._session = ort.InferenceSession(model_path)
                self._available = True
            except Exception:
                self._session = None
                self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def score_audio(self, pcm_bytes: bytes, sample_rate: int = 16000) -> AntiSpoofResult:
        """Infers spoof score via ONNX model or falls back to AcousticArtifactDetector."""
        if not self._available or self._session is None:
            return self.fallback.score_audio(pcm_bytes, sample_rate=sample_rate)

        # Prepare normalized float array for model input (zero disk writes)
        count = len(pcm_bytes) // 2
        if count == 0:
            return self.fallback.score_audio(pcm_bytes, sample_rate=sample_rate)

        samples = struct.unpack(f"<{count}h", pcm_bytes[: count * 2])
        float_waveform = [s / 32768.0 for s in samples]

        try:
            import numpy as np  # type: ignore
            input_name = self._session.get_inputs()[0].name
            input_tensor = np.array([float_waveform], dtype=np.float32)
            outputs = self._session.run(None, {input_name: input_tensor})
            # Assume 2-class logits [bonafide, spoof]
            logits = outputs[0][0]
            # Softmax
            exp_spoof = math.exp(logits[1])
            s_a = exp_spoof / (math.exp(logits[0]) + exp_spoof)
            feats = self.fallback.extractor.extract(pcm_bytes, sample_rate)
            return AntiSpoofResult(
                s_a=round(s_a, 4),
                features=feats,
                engine_name="ONNXRTAntiSpoofEngine",
                is_synthetic=(s_a >= 0.70),
                is_suspicious=(s_a >= 0.40),
                artifacts_detected=["onnx_model_inference"],
                is_mock=False,
            )
        except Exception:
            return self.fallback.score_audio(pcm_bytes, sample_rate=sample_rate)


class MockAntiSpoofEngine:
    """Deterministic in-memory mock engine for testing and CI."""

    def __init__(self, default_score: float = 0.10) -> None:
        self.default_score = default_score
        self._scripted_scores: Dict[int, float] = {}

    def register_score_for_length(self, byte_length: int, score: float) -> None:
        """Maps a specific audio byte count to a defined acoustic score."""
        self._scripted_scores[byte_length] = score

    def score_audio(self, pcm_bytes: bytes, sample_rate: int = 16000) -> AntiSpoofResult:
        """Returns scripted or default risk score."""
        score = self._scripted_scores.get(len(pcm_bytes), self.default_score)
        extractor = AcousticFeatureExtractor()
        feats = extractor.extract(pcm_bytes, sample_rate)
        return AntiSpoofResult(
            s_a=round(score, 4),
            features=feats,
            engine_name="MockAntiSpoofEngine",
            is_synthetic=(score >= 0.70),
            is_suspicious=(score >= 0.40),
            artifacts_detected=["mock_trigger"] if score >= 0.40 else [],
            is_mock=True,
        )


def create_antispoof_engine(
    engine_type: str = "auto",
    model_path: Optional[str] = None,
) -> BaseAntiSpoofEngine:
    """Factory creating appropriate anti-spoofing engine instance."""
    if engine_type == "mock":
        return MockAntiSpoofEngine()
    if engine_type in ("auto", "onnx") and model_path:
        onnx_eng = ONNXAntiSpoofEngine(model_path=model_path)
        if onnx_eng.is_available:
            return onnx_eng
    return AcousticArtifactDetector()
