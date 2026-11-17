"""In-memory circular PCM audio ring buffer and chunker with VAD hook.

Conforms to Rule 7: Zero raw audio bytes are ever persisted to disk.
Processes 16 kHz 16-bit mono linear PCM into overlapping 3.0-second windows.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from typing import Generator, List, Optional


@dataclass(frozen=True)
class AudioChunk:
    """Represents a clean, extracted time window of PCM audio for ML analysis."""
    chunk_index: int
    timestamp_sec: float
    data: bytes
    duration_sec: float
    sample_rate: int
    channels: int
    rms_energy: float
    has_speech: bool

    @property
    def sample_count(self) -> int:
        return len(self.data) // 2


class SimpleEnergyVAD:
    """Energy-based Voice Activity Detection hook for 16-bit linear PCM audio."""

    def __init__(self, energy_threshold: float = 0.015) -> None:
        """
        Args:
            energy_threshold: Normalized RMS threshold [0.0 - 1.0].
                              Default 0.015 rejects baseline background silence/hiss.
        """
        self.energy_threshold = energy_threshold

    def calculate_rms(self, pcm_bytes: bytes) -> float:
        """Calculates normalized RMS amplitude [0.0, 1.0] from 16-bit signed PCM."""
        if not pcm_bytes or len(pcm_bytes) < 2:
            return 0.0

        sample_count = len(pcm_bytes) // 2
        # Unpack signed 16-bit integers
        fmt = f"<{sample_count}h"
        try:
            samples = struct.unpack(fmt, pcm_bytes[:sample_count * 2])
        except struct.error:
            return 0.0

        sum_squares = sum(s * s for s in samples)
        mean_square = sum_squares / sample_count
        rms = math.sqrt(mean_square)
        return rms / 32768.0

    def is_speech(self, pcm_bytes: bytes) -> tuple[bool, float]:
        """Returns (has_speech, normalized_rms)."""
        rms = self.calculate_rms(pcm_bytes)
        return (rms >= self.energy_threshold, rms)


class AudioChunker:
    """Circular in-memory ring buffer that segments streaming PCM into sliding chunks."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2,
        chunk_duration_sec: float = 3.0,
        chunk_stride_sec: float = 1.0,
        max_buffer_sec: float = 12.0,
        vad_hook: Optional[SimpleEnergyVAD] = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width
        self.chunk_duration_sec = chunk_duration_sec
        self.chunk_stride_sec = chunk_stride_sec

        self.bytes_per_second = sample_rate * channels * sample_width
        self.chunk_bytes = int(chunk_duration_sec * self.bytes_per_second)
        self.stride_bytes = int(chunk_stride_sec * self.bytes_per_second)
        self.max_buffer_bytes = int(max_buffer_sec * self.bytes_per_second)

        self.vad = vad_hook or SimpleEnergyVAD()

        # In-memory byte buffer
        self._buffer = bytearray()
        self._total_bytes_received: int = 0
        self._chunks_emitted: int = 0

    @property
    def buffered_seconds(self) -> float:
        return len(self._buffer) / self.bytes_per_second

    @property
    def chunks_emitted(self) -> int:
        return self._chunks_emitted

    @property
    def total_bytes_received(self) -> int:
        return self._total_bytes_received

    def push_pcm(self, pcm_bytes: bytes) -> List[AudioChunk]:
        """Appends incoming raw PCM frame and yields any newly completed chunks."""
        if not pcm_bytes:
            return []

        # Enforce 2-byte boundary alignment
        if len(pcm_bytes) % self.sample_width != 0:
            valid_len = (len(pcm_bytes) // self.sample_width) * self.sample_width
            pcm_bytes = pcm_bytes[:valid_len]

        self._buffer.extend(pcm_bytes)
        self._total_bytes_received += len(pcm_bytes)

        # Evict oldest bytes if buffer exceeds max capacity to prevent memory bloat
        if len(self._buffer) > self.max_buffer_bytes:
            excess = len(self._buffer) - self.max_buffer_bytes
            # Align eviction to stride
            evict_bytes = ((excess // self.stride_bytes) + 1) * self.stride_bytes
            del self._buffer[:evict_bytes]

        chunks: List[AudioChunk] = []

        # Sliding window loop: extract while we have at least chunk_bytes
        while len(self._buffer) >= self.chunk_bytes:
            chunk_data = bytes(self._buffer[:self.chunk_bytes])

            has_speech, rms = self.vad.is_speech(chunk_data)
            timestamp = (self._chunks_emitted * self.chunk_stride_sec) + self.chunk_duration_sec

            chunk = AudioChunk(
                chunk_index=self._chunks_emitted,
                timestamp_sec=round(timestamp, 2),
                data=chunk_data,
                duration_sec=self.chunk_duration_sec,
                sample_rate=self.sample_rate,
                channels=self.channels,
                rms_energy=round(rms, 4),
                has_speech=has_speech,
            )
            chunks.append(chunk)
            self._chunks_emitted += 1

            # Advance buffer by stride_bytes
            del self._buffer[:self.stride_bytes]

        return chunks

    def reset(self) -> None:
        """Clears all buffered audio and resets chunk counters."""
        self._buffer.clear()
        self._total_bytes_received = 0
        self._chunks_emitted = 0
