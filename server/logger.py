"""Privacy-preserving structured logger for Family Voice Shield.

Enforces Rule 7: Zero raw audio bytes, transcripts, or credentials in log output.
All logs format as structured JSON with event metadata and timing.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any, Dict

# Forbidden keys that must never appear in log payloads
SENSITIVE_KEYS = frozenset({
    "audio", "raw_audio", "pcm", "bytes", "transcript", "text", "speech",
    "secret", "key", "totp", "code", "phone", "phone_number", "contact", "e164"
})


class StructuredJsonFormatter(logging.Formatter):
    """JSON formatter formatting standard log records with custom attributes."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include structured extra fields if passed via extra={}
        if hasattr(record, "structured_data") and isinstance(record.structured_data, dict):
            for k, v in record.structured_data.items():
                if k.lower() not in SENSITIVE_KEYS:
                    payload[k] = v

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level_name: str = "INFO") -> None:
    """Configures the root logger with the structured JSON formatter."""
    root_logger = logging.getLogger("fvs")
    root_logger.setLevel(getattr(logging, level_name.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(handler)
    root_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Returns a namespaced child logger under 'fvs'."""
    return logging.getLogger(f"fvs.{name}")


def log_event(
    logger: logging.Logger,
    level: int,
    event_type: str,
    message: str,
    session_id: str | None = None,
    **kwargs: Any
) -> None:
    """Logs a structured event while strictly sanitizing sensitive fields."""
    sanitized: Dict[str, Any] = {
        "event_type": event_type,
    }
    if session_id:
        sanitized["session_id"] = session_id

    for k, v in kwargs.items():
        if k.lower() not in SENSITIVE_KEYS:
            sanitized[k] = v

    logger.log(level, message, extra={"structured_data": sanitized})
