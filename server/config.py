"""Configuration loader for Family Voice Shield streaming server.

Reads environment variables with sensible defaults for 16 kHz PCM audio streaming,
in-memory ring buffering, session lifetimes, and CORS settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

try:
    from dotenv import load_dotenv  # type: ignore
    _HAS_DOTENV = True
except ImportError:
    _HAS_DOTENV = False


@dataclass(frozen=True)
class ServerConfig:
    """Immutable server configuration parameters."""

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Audio Stream Parameters (16 kHz, 16-bit signed integer linear PCM, Mono)
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2  # 2 bytes per sample (16-bit)
    frame_duration_ms: int = 100  # 100ms per client packet (3200 bytes)

    # Chunker Parameters (3.0s window, 1.0s hop/stride)
    chunk_duration_sec: float = 3.0
    chunk_stride_sec: float = 1.0

    # Session Management
    session_ttl_sec: int = 3600
    max_active_sessions: int = 100

    # Security & Logging
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    log_level: str = "INFO"

    @property
    def bytes_per_second(self) -> int:
        """Total raw PCM bytes per second of audio."""
        return self.sample_rate * self.channels * self.sample_width

    @property
    def frame_bytes(self) -> int:
        """Expected byte length of a single client binary PCM frame (100ms)."""
        return int((self.frame_duration_ms / 1000.0) * self.bytes_per_second)

    @property
    def chunk_bytes(self) -> int:
        """Total byte size of a 3.0-second chunk (e.g. 96,000 bytes at 16kHz 16-bit mono)."""
        return int(self.chunk_duration_sec * self.bytes_per_second)

    @property
    def stride_bytes(self) -> int:
        """Byte offset between consecutive analysis chunk windows (e.g. 32,000 bytes)."""
        return int(self.chunk_stride_sec * self.bytes_per_second)


def _parse_bool(val: str) -> bool:
    return val.strip().lower() in ("1", "true", "yes", "on")


def load_config(env_path: Optional[str] = None) -> ServerConfig:
    """Loads server configuration from environment variables and optional .env file."""
    if _HAS_DOTENV:
        load_dotenv(dotenv_path=env_path)
    elif env_path and os.path.exists(env_path):
        # Fallback simple .env reader if python-dotenv is not installed
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

    cors_raw = os.getenv("FVS_CORS_ORIGINS", "*")
    cors_list = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]

    return ServerConfig(
        host=os.getenv("FVS_HOST", "0.0.0.0"),
        port=int(os.getenv("FVS_PORT", "8000")),
        debug=_parse_bool(os.getenv("FVS_DEBUG", "false")),
        sample_rate=int(os.getenv("FVS_SAMPLE_RATE", "16000")),
        channels=int(os.getenv("FVS_CHANNELS", "1")),
        sample_width=int(os.getenv("FVS_SAMPLE_WIDTH", "2")),
        frame_duration_ms=int(os.getenv("FVS_FRAME_DURATION_MS", "100")),
        chunk_duration_sec=float(os.getenv("FVS_CHUNK_DURATION_SEC", "3.0")),
        chunk_stride_sec=float(os.getenv("FVS_CHUNK_STRIDE_SEC", "1.0")),
        session_ttl_sec=int(os.getenv("FVS_SESSION_TTL_SEC", "3600")),
        max_active_sessions=int(os.getenv("FVS_MAX_ACTIVE_SESSIONS", "100")),
        cors_origins=cors_list,
        log_level=os.getenv("FVS_LOG_LEVEL", "INFO").upper(),
    )
