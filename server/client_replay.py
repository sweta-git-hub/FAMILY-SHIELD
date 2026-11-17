"""Audio streaming replay client for Family Voice Shield.

Emulates mobile client microphone capture:
1. Requests ephemeral session token via POST /v1/session.
2. Establishes WebSocket stream at /v1/stream?token=...
3. Sends handshake and call context frames.
4. Streams 16 kHz 16-bit linear PCM audio in paced 100ms binary frames.
5. Measures and records round-trip latency for received score frames.
6. Cleanly terminates with end control frame.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import struct
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    import websockets  # type: ignore
    _HAS_WEBSOCKETS = True
except ImportError:
    _HAS_WEBSOCKETS = False


@dataclass
class StreamStats:
    """Statistics gathered during an audio streaming session."""
    session_id: str = ""
    frames_sent: int = 0
    bytes_sent: int = 0
    scores_received: int = 0
    latencies_ms: List[float] = field(default_factory=list)
    final_tier: str = "GREEN"
    final_risk: float = 0.0

    @property
    def avg_latency_ms(self) -> float:
        return sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def max_latency_ms(self) -> float:
        return max(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def min_latency_ms(self) -> float:
        return min(self.latencies_ms) if self.latencies_ms else 0.0


def request_session(http_url: str, role: str = "guardian", lang: str = "hi") -> Dict[str, Any]:
    """Requests a transient session token via HTTP POST /v1/session."""
    endpoint = f"{http_url.rstrip('/')}/v1/session"
    payload = json.dumps({
        "device_role": role,
        "lang": lang,
        "client_version": "0.4.0",
    }).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 201:
            raise RuntimeError(f"Session request failed with status {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def generate_synthetic_stream(duration_sec: float, sample_rate: int = 16000, freq_hz: float = 440.0) -> bytes:
    """Generates synthetic 16 kHz 16-bit mono linear PCM audio."""
    total_samples = int(duration_sec * sample_rate)
    samples = []
    max_amp = 32767 * 0.45
    for i in range(total_samples):
        # Alternate speech-like bursts and pauses
        mod = math.sin(2 * math.pi * 2.0 * (i / sample_rate))
        if mod > 0.1:
            val = int(max_amp * math.sin(2 * math.pi * freq_hz * (i / sample_rate)))
        else:
            val = 0
        samples.append(val)
    return struct.pack(f"<{len(samples)}h", *samples)


def read_wav_pcm(file_path: str) -> tuple[bytes, int, int]:
    """Reads raw PCM bytes from a 16-bit mono WAV file."""
    import wave
    with wave.open(file_path, "rb") as wf:
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())

        if sample_width != 2:
            raise ValueError(f"WAV must be 16-bit PCM (sample_width=2), got {sample_width}")
        return frames, sample_rate, channels


async def run_audio_stream(
    server_host: str = "localhost",
    server_port: int = 8000,
    duration_sec: float = 10.0,
    audio_file: Optional[str] = None,
    unknown_number: bool = True,
    claims_relative: bool = True,
) -> StreamStats:
    """Streams audio frames over WebSocket and collects performance metrics."""
    if not _HAS_WEBSOCKETS:
        raise RuntimeError("websockets package required for streaming client. Run pip install websockets.")

    http_url = f"http://{server_host}:{server_port}"
    ws_base_url = f"ws://{server_host}:{server_port}"

    stats = StreamStats()

    # 1. Acquire ephemeral session token
    session_data = request_session(http_url)
    session_id = session_data["session_id"]
    token = session_data["token"]
    ws_endpoint = f"{ws_base_url}/v1/stream?token={token}"

    stats.session_id = session_id

    # 2. Prepare audio PCM data
    if audio_file:
        pcm_data, sr, channels = read_wav_pcm(audio_file)
    else:
        pcm_data = generate_synthetic_stream(duration_sec=duration_sec, sample_rate=16000)

    # Split into 100ms frames (1600 samples * 2 bytes = 3200 bytes)
    frame_bytes = 3200
    frames = [pcm_data[i:i + frame_bytes] for i in range(0, len(pcm_data), frame_bytes)]

    # 3. Connect to WebSocket stream
    async with websockets.connect(ws_endpoint) as ws:
        # Handshake frame
        await ws.send(json.dumps({
            "type": "start",
            "session": session_id,
            "lang": "hi",
            "sr": 16000,
            "channels": 1,
        }))

        # Wait for ready acknowledgment
        ready_resp = json.loads(await ws.recv())
        if ready_resp.get("type") != "ready":
            raise RuntimeError(f"Expected 'ready' frame, received: {ready_resp}")

        # Send call context
        await ws.send(json.dumps({
            "type": "context",
            "unknown_number": unknown_number,
            "claims_relative": claims_relative,
            "hour": time.localtime().tm_hour,
        }))

        # Task to listen for real-time scores
        pending_send_times: Dict[int, float] = {}

        async def score_listener() -> None:
            try:
                async for message in ws:
                    recv_time = time.time()
                    data = json.loads(message)
                    if data.get("type") == "score":
                        stats.scores_received += 1
                        stats.final_tier = data.get("tier", "GREEN")
                        stats.final_risk = data.get("risk", 0.0)

                        # Match latency against nearest pending send
                        if pending_send_times:
                            earliest_idx = min(pending_send_times.keys())
                            latency = (recv_time - pending_send_times.pop(earliest_idx)) * 1000.0
                            stats.latencies_ms.append(round(latency, 2))
            except websockets.exceptions.ConnectionClosed:
                pass

        listener_task = asyncio.create_task(score_listener())

        # Stream paced 100ms frames
        for idx, frame in enumerate(frames):
            send_time = time.time()
            pending_send_times[idx] = send_time

            await ws.send(frame)
            stats.frames_sent += 1
            stats.bytes_sent += len(frame)

            # Paced transmission (100ms per packet)
            await asyncio.sleep(0.10)

        # Allow final chunks to flush and score
        await asyncio.sleep(1.2)

        # Teardown
        await ws.send(json.dumps({"type": "end"}))
        await listener_task

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Family Voice Shield Audio Replay Client")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--duration", type=float, default=10.0, help="Duration to stream in seconds")
    parser.add_argument("--file", default=None, help="Path to 16kHz WAV file")
    args = parser.parse_args()

    print(f"[*] Starting audio streaming client connecting to {args.host}:{args.port}...")
    stats = asyncio.run(run_audio_stream(
        server_host=args.host,
        server_port=args.port,
        duration_sec=args.duration,
        audio_file=args.file,
    ))

    print(f"[+] Stream Complete for session: {stats.session_id}")
    print(f"    Frames Sent:     {stats.frames_sent} ({stats.bytes_sent} bytes)")
    print(f"    Scores Received: {stats.scores_received}")
    print(f"    Avg Latency:     {stats.avg_latency_ms:.1f} ms")
    print(f"    Min/Max Latency: {stats.min_latency_ms:.1f} ms / {stats.max_latency_ms:.1f} ms")
    print(f"    Final Tier:      {stats.final_tier} (Risk: {stats.final_risk})")


if __name__ == "__main__":
    main()
