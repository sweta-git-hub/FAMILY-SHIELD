"""Telephony Codec & Channel Degradation Simulator for Family Voice Shield.

Simulates carrier telephony channel artifacts on 16 kHz linear PCM audio:
1. G.711 mu-law (PCMU) & A-law (PCMA) 8-bit companding (RFC 3551)
2. 8 kHz narrowband downsampling & linear interpolation upsampling
3. 300 Hz - 3400 Hz telephony voice bandpass filtering
4. Network packet loss and jitter simulation

Enables anti-spoofing models to test resilience against telephony compression
without triggering false-positive synthetic alarms on natural carrier speech.
Zero disk persistence (Rule 7).
"""

from __future__ import annotations

import math
import random
import struct
from dataclasses import dataclass
from typing import List, Tuple


# Precomputed G.711 mu-law conversion tables for performance
# 16-bit signed int (-32768 to 32767) -> 8-bit mu-law byte (0 to 255)
# and reverse 8-bit mu-law byte -> 16-bit signed int
BIAS = 0x84  # 132
CLIP = 32635


def linear_to_ulaw(sample: int) -> int:
    """Converts a 16-bit signed linear PCM sample to an 8-bit mu-law byte.
    
    Standard ITU-T G.711 / RFC 3551 implementation.
    """
    sign = 0x80 if sample < 0 else 0x00
    if sample < 0:
        sample = -sample
    if sample > CLIP:
        sample = CLIP

    sample += BIAS
    exponent = 7
    for exp, mask in enumerate((0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200, 0x0100)):
        if sample & mask:
            exponent = 7 - exp
            break
    else:
        exponent = 0

    mantissa = (sample >> (exponent + 3)) & 0x0F
    ulaw_byte = ~(sign | (exponent << 4) | mantissa) & 0xFF
    return ulaw_byte


def ulaw_to_linear(ulaw_byte: int) -> int:
    """Converts an 8-bit mu-law byte to a 16-bit signed linear PCM sample."""
    ulaw_byte = ~ulaw_byte & 0xFF
    sign = -1 if (ulaw_byte & 0x80) else 1
    exponent = (ulaw_byte >> 4) & 0x07
    mantissa = ulaw_byte & 0x0F
    sample = ((mantissa << 3) + BIAS) << exponent
    sample -= BIAS
    return sign * sample


def linear_to_alaw(sample: int) -> int:
    """Converts a 16-bit signed linear PCM sample to an 8-bit A-law byte."""
    sign = 0x80 if sample >= 0 else 0x00
    if sample < 0:
        sample = -sample
    if sample > 32767:
        sample = 32767

    if sample >= 256:
        exponent = 7
        for exp, mask in enumerate((0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200)):
            if sample & mask:
                exponent = 7 - exp
                break
        else:
            exponent = 1
        mantissa = (sample >> (exponent + 3)) & 0x0F
    else:
        exponent = 0
        mantissa = (sample >> 4) & 0x0F

    alaw_byte = (sign | (exponent << 4) | mantissa) ^ 0xD5
    return alaw_byte & 0xFF


def alaw_to_linear(alaw_byte: int) -> int:
    """Converts an 8-bit A-law byte to a 16-bit signed linear PCM sample."""
    alaw_byte ^= 0xD5
    sign = 1 if (alaw_byte & 0x80) else -1
    exponent = (alaw_byte >> 4) & 0x07
    mantissa = alaw_byte & 0x0F
    if exponent == 0:
        sample = (mantissa << 4) + 8
    else:
        sample = ((mantissa << 4) + 0x108) << (exponent - 1)
    return sign * sample


class TelephonyBandpassFilter:
    """IIR digital filter approximating standard 300 Hz - 3400 Hz voice telephony band."""

    def __init__(self, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate
        # 2nd order Butterworth highpass (300 Hz) and lowpass (3400 Hz) coefficients
        self._init_coefficients()

    def _init_coefficients(self) -> None:
        # High-pass filter at 300 Hz
        f_hp = 300.0 / self.sample_rate
        q = 0.7071
        omega_hp = math.tan(math.pi * f_hp)
        norm_hp = 1.0 / (1.0 + omega_hp / q + omega_hp * omega_hp)
        self.hp_b0 = norm_hp
        self.hp_b1 = -2.0 * norm_hp
        self.hp_b2 = norm_hp
        self.hp_a1 = 2.0 * (omega_hp * omega_hp - 1.0) * norm_hp
        self.hp_a2 = (1.0 - omega_hp / q + omega_hp * omega_hp) * norm_hp

        # Low-pass filter at 3400 Hz
        f_lp = 3400.0 / self.sample_rate
        omega_lp = math.tan(math.pi * f_lp)
        norm_lp = 1.0 / (1.0 + omega_lp / q + omega_lp * omega_lp)
        self.lp_b0 = omega_lp * omega_lp * norm_lp
        self.lp_b1 = 2.0 * self.lp_b0
        self.lp_b2 = self.lp_b0
        self.lp_a1 = 2.0 * (omega_lp * omega_lp - 1.0) * norm_lp
        self.lp_a2 = (1.0 - omega_lp / q + omega_lp * omega_lp) * norm_lp

    def filter_samples(self, samples: List[int]) -> List[int]:
        """Applies cascaded HPF and LPF to linear PCM integer samples."""
        if not samples:
            return []

        # 1. Apply Highpass (300 Hz)
        hp_out: List[float] = [0.0] * len(samples)
        x1 = x2 = y1 = y2 = 0.0
        for i, s in enumerate(samples):
            x0 = float(s)
            y0 = (
                self.hp_b0 * x0
                + self.hp_b1 * x1
                + self.hp_b2 * x2
                - self.hp_a1 * y1
                - self.hp_a2 * y2
            )
            hp_out[i] = y0
            x2, x1 = x1, x0
            y2, y1 = y1, y0

        # 2. Apply Lowpass (3400 Hz)
        result: List[int] = [0] * len(samples)
        x1 = x2 = y1 = y2 = 0.0
        for i, s in enumerate(hp_out):
            x0 = s
            y0 = (
                self.lp_b0 * x0
                + self.lp_b1 * x1
                + self.lp_b2 * x2
                - self.lp_a1 * y1
                - self.lp_a2 * y2
            )
            clamped = max(-32768, min(32767, int(round(y0))))
            result[i] = clamped
            x2, x1 = x1, x0
            y2, y1 = y1, y0

        return result


class TelephonyCodecSimulator:
    """Comprehensive telephony codec and channel simulator."""

    def __init__(self, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate
        self.bandpass = TelephonyBandpassFilter(sample_rate=sample_rate)

    def pcm_to_samples(self, pcm_bytes: bytes) -> List[int]:
        """Unpacks 16-bit signed little-endian PCM bytes into integer sample list."""
        count = len(pcm_bytes) // 2
        if count == 0:
            return []
        return list(struct.unpack(f"<{count}h", pcm_bytes[: count * 2]))

    def samples_to_pcm(self, samples: List[int]) -> bytes:
        """Packs integer sample list into 16-bit signed little-endian PCM bytes."""
        clamped = [max(-32768, min(32767, int(s))) for s in samples]
        return struct.pack(f"<{len(clamped)}h", *clamped)

    def encode_ulaw(self, pcm_bytes: bytes) -> bytes:
        """Encodes 16-bit PCM bytes to G.711 mu-law bytes."""
        samples = self.pcm_to_samples(pcm_bytes)
        return bytes(linear_to_ulaw(s) for s in samples)

    def decode_ulaw(self, ulaw_bytes: bytes) -> bytes:
        """Decodes G.711 mu-law bytes back to 16-bit linear PCM bytes."""
        samples = [ulaw_to_linear(b) for b in ulaw_bytes]
        return self.samples_to_pcm(samples)

    def encode_alaw(self, pcm_bytes: bytes) -> bytes:
        """Encodes 16-bit PCM bytes to G.711 A-law bytes."""
        samples = self.pcm_to_samples(pcm_bytes)
        return bytes(linear_to_alaw(s) for s in samples)

    def decode_alaw(self, alaw_bytes: bytes) -> bytes:
        """Decodes G.711 A-law bytes back to 16-bit linear PCM bytes."""
        samples = [alaw_to_linear(b) for b in alaw_bytes]
        return self.samples_to_pcm(samples)

    def resample_16k_to_8k(self, samples_16k: List[int]) -> List[int]:
        """Downsamples 16 kHz samples to 8 kHz using moving average decimation."""
        if len(samples_16k) < 2:
            return samples_16k[:]
        # 2:1 decimation with 2-sample antialiasing filter
        out: List[int] = []
        for i in range(0, len(samples_16k) - 1, 2):
            avg = (samples_16k[i] + samples_16k[i + 1]) // 2
            out.append(avg)
        return out

    def resample_8k_to_16k(self, samples_8k: List[int]) -> List[int]:
        """Upsamples 8 kHz samples back to 16 kHz using linear interpolation."""
        if not samples_8k:
            return []
        out: List[int] = []
        for i in range(len(samples_8k) - 1):
            s0 = samples_8k[i]
            s1 = samples_8k[i + 1]
            out.append(s0)
            out.append((s0 + s1) // 2)
        out.append(samples_8k[-1])
        out.append(samples_8k[-1])
        return out

    def simulate_packet_loss(
        self,
        samples: List[int],
        loss_rate: float = 0.03,
        packet_samples: int = 160,
    ) -> List[int]:
        """Simulates VoIP/VoLTE packet loss by replacing lost frames with silence/attenuation."""
        if loss_rate <= 0.0 or not samples:
            return samples[:]

        out = samples[:]
        num_packets = len(out) // packet_samples
        for p in range(num_packets):
            if random.random() < loss_rate:
                start = p * packet_samples
                end = min(start + packet_samples, len(out))
                for idx in range(start, end):
                    out[idx] = 0  # Packet drop / silence insertion
        return out

    def simulate_telephony_channel(
        self,
        pcm_bytes: bytes,
        codec: str = "g711_ulaw",
        apply_bandpass: bool = True,
        simulate_loss: bool = True,
        packet_loss_rate: float = 0.02,
    ) -> bytes:
        """Full telephony pipeline simulation on raw 16 kHz PCM bytes.
        
        Applies:
        1. 300 - 3400 Hz voice bandpass filter
        2. Downsampling to 8 kHz carrier rate
        3. G.711 mu-law or A-law non-linear quantisation and expansion
        4. Optional packet loss / jitter simulation
        5. Upsampling back to 16 kHz
        """
        if not pcm_bytes:
            return b""

        samples = self.pcm_to_samples(pcm_bytes)

        # 1. Bandpass filter
        if apply_bandpass:
            samples = self.bandpass.filter_samples(samples)

        # 2. Downsample 16k -> 8k
        samples_8k = self.resample_16k_to_8k(samples)

        # 3. G.711 Codec Quantisation
        if codec == "g711_alaw":
            companded = [linear_to_alaw(s) for s in samples_8k]
            quantised_8k = [alaw_to_linear(b) for b in companded]
        else:
            companded = [linear_to_ulaw(s) for s in samples_8k]
            quantised_8k = [ulaw_to_linear(b) for b in companded]

        # 4. Packet loss simulation
        if simulate_loss and packet_loss_rate > 0.0:
            quantised_8k = self.simulate_packet_loss(quantised_8k, loss_rate=packet_loss_rate)

        # 5. Upsample back to 16k
        restored_16k = self.resample_8k_to_16k(quantised_8k)

        # Match exact input byte length
        target_sample_count = len(pcm_bytes) // 2
        if len(restored_16k) > target_sample_count:
            restored_16k = restored_16k[:target_sample_count]
        elif len(restored_16k) < target_sample_count:
            restored_16k.extend([0] * (target_sample_count - len(restored_16k)))

        return self.samples_to_pcm(restored_16k)
