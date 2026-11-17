"""Unit tests for AudioChunker and SimpleEnergyVAD."""

import math
import struct
import unittest
from server.chunker import AudioChunker, SimpleEnergyVAD


def generate_sine_pcm(freq_hz: float, duration_sec: float, sample_rate: int = 16000, amp: float = 0.5) -> bytes:
    """Generates synthetic 16-bit PCM mono sine wave for testing."""
    sample_count = int(duration_sec * sample_rate)
    samples = []
    max_val = 32767 * amp
    for i in range(sample_count):
        val = int(max_val * math.sin(2 * math.pi * freq_hz * (i / sample_rate)))
        samples.append(val)
    return struct.pack(f"<{len(samples)}h", *samples)


def generate_silence_pcm(duration_sec: float, sample_rate: int = 16000) -> bytes:
    """Generates pure silence PCM (all zeros)."""
    sample_count = int(duration_sec * sample_rate)
    return b"\x00" * (sample_count * 2)


class TestAudioChunker(unittest.TestCase):

    def setUp(self) -> None:
        self.chunker = AudioChunker(
            sample_rate=16000,
            channels=1,
            sample_width=2,
            chunk_duration_sec=3.0,
            chunk_stride_sec=1.0,
            max_buffer_sec=6.0,
        )

    def test_chunker_initial_state(self) -> None:
        self.assertEqual(self.chunker.buffered_seconds, 0.0)
        self.assertEqual(self.chunker.chunks_emitted, 0)
        self.assertEqual(self.chunker.total_bytes_received, 0)

    def test_single_chunk_generation(self) -> None:
        # 16000 * 2 = 32000 bytes per second
        # 3.0 seconds = 96000 bytes
        audio = generate_sine_pcm(freq_hz=440.0, duration_sec=3.0)
        chunks = self.chunker.push_pcm(audio)

        self.assertEqual(len(chunks), 1)
        chunk = chunks[0]
        self.assertEqual(chunk.chunk_index, 0)
        self.assertEqual(len(chunk.data), 96000)
        self.assertEqual(chunk.sample_count, 48000)
        self.assertEqual(chunk.duration_sec, 3.0)
        self.assertTrue(chunk.has_speech)
        self.assertGreater(chunk.rms_energy, 0.1)

    def test_sliding_window_and_overlap(self) -> None:
        # 4.0 seconds of audio should produce 2 chunks (stride=1.0s, window=3.0s)
        audio = generate_sine_pcm(freq_hz=440.0, duration_sec=4.0)
        chunks = self.chunker.push_pcm(audio)

        self.assertEqual(len(chunks), 2)
        chunk0, chunk1 = chunks[0], chunks[1]

        self.assertEqual(chunk0.chunk_index, 0)
        self.assertEqual(chunk1.chunk_index, 1)

        # 2.0s overlap = 64000 bytes
        overlap_bytes = int(2.0 * 32000)
        self.assertEqual(chunk0.data[-overlap_bytes:], chunk1.data[:overlap_bytes])

    def test_incremental_streaming_packets(self) -> None:
        # Simulate client sending 100ms packets (3200 bytes each)
        packet = generate_sine_pcm(freq_hz=440.0, duration_sec=0.1)
        self.assertEqual(len(packet), 3200)

        emitted_chunks = []
        for i in range(35):  # 3.5 seconds total
            chunks = self.chunker.push_pcm(packet)
            emitted_chunks.extend(chunks)

        # At 3.0s: Chunk 0 emitted. At 3.5s: Buffer has 2.5s remaining, no chunk yet.
        self.assertEqual(len(emitted_chunks), 1)
        self.assertEqual(self.chunker.chunks_emitted, 1)

    def test_silence_vad_detection(self) -> None:
        silence = generate_silence_pcm(duration_sec=3.0)
        chunks = self.chunker.push_pcm(silence)

        self.assertEqual(len(chunks), 1)
        chunk = chunks[0]
        self.assertFalse(chunk.has_speech)
        self.assertEqual(chunk.rms_energy, 0.0)

    def test_buffer_capacity_eviction(self) -> None:
        # Max buffer is 6.0 seconds (192,000 bytes)
        # Push 10.0 seconds of audio all at once
        big_audio = generate_sine_pcm(freq_hz=440.0, duration_sec=10.0)
        chunks = self.chunker.push_pcm(big_audio)

        self.assertGreaterEqual(len(chunks), 8)
        self.assertLessEqual(self.chunker.buffered_seconds, 6.0)

    def test_reset_clears_state(self) -> None:
        self.chunker.push_pcm(generate_sine_pcm(freq_hz=440.0, duration_sec=3.0))
        self.assertEqual(self.chunker.chunks_emitted, 1)

        self.chunker.reset()
        self.assertEqual(self.chunker.chunks_emitted, 0)
        self.assertEqual(self.chunker.buffered_seconds, 0.0)
        self.assertEqual(self.chunker.total_bytes_received, 0)


class TestSimpleEnergyVAD(unittest.TestCase):

    def setUp(self) -> None:
        self.vad = SimpleEnergyVAD(energy_threshold=0.015)

    def test_silence_rms_is_zero(self) -> None:
        silence = generate_silence_pcm(duration_sec=1.0)
        has_speech, rms = self.vad.is_speech(silence)
        self.assertFalse(has_speech)
        self.assertEqual(rms, 0.0)

    def test_active_speech_rms_above_threshold(self) -> None:
        speech = generate_sine_pcm(freq_hz=440.0, duration_sec=1.0, amp=0.4)
        has_speech, rms = self.vad.is_speech(speech)
        self.assertTrue(has_speech)
        self.assertGreater(rms, 0.015)


if __name__ == "__main__":
    unittest.main()
