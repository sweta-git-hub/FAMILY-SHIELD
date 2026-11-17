"""Transient session manager and endpoint for Family Voice Shield streaming.

Enforces zero-knowledge ephemeral session tracking in memory.
No database, no disk storage, and sessions automatically expire after TTL.
"""

from __future__ import annotations

import secrets
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    from fastapi import APIRouter, HTTPException, Request, status  # type: ignore
    from pydantic import BaseModel, Field  # type: ignore
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False

from server.logger import get_logger, log_event

logger = get_logger("session")


@dataclass
class SessionRecord:
    """Ephemeral in-memory session metadata."""
    session_id: str
    token: str
    device_role: str
    lang: str
    created_at: float
    expires_at: float
    is_active: bool = False
    chunks_processed: int = 0
    last_activity: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class SessionManager:
    """Thread-safe in-memory session registry with automated TTL expiration."""

    def __init__(self, max_active_sessions: int = 100, default_ttl_sec: int = 3600) -> None:
        self.max_active_sessions = max_active_sessions
        self.default_ttl_sec = default_ttl_sec
        self._sessions_by_token: Dict[str, SessionRecord] = {}
        self._tokens_by_session_id: Dict[str, str] = {}

    @property
    def active_count(self) -> int:
        self.cleanup_expired()
        return len(self._sessions_by_token)

    def create_session(
        self,
        device_role: str = "guardian",
        lang: str = "auto",
        ttl_sec: Optional[int] = None
    ) -> SessionRecord:
        """Creates a new ephemeral streaming session and issues a secure bearer token."""
        self.cleanup_expired()

        if len(self._sessions_by_token) >= self.max_active_sessions:
            log_event(logger, 30, "session_limit_exceeded", "Maximum active sessions reached", max_sessions=self.max_active_sessions)
            raise ValueError(f"Server capacity reached: {self.max_active_sessions} concurrent sessions maximum.")

        session_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(32)
        ttl = ttl_sec if ttl_sec is not None else self.default_ttl_sec
        now = time.time()

        record = SessionRecord(
            session_id=session_id,
            token=token,
            device_role=device_role,
            lang=lang,
            created_at=now,
            expires_at=now + ttl,
            last_activity=now,
        )

        self._sessions_by_token[token] = record
        self._tokens_by_session_id[session_id] = token

        log_event(
            logger,
            20,
            "session_created",
            "Streaming session created",
            session_id=session_id,
            device_role=device_role,
            lang=lang,
            ttl_sec=ttl,
        )
        return record

    def validate_token(self, token: str) -> Optional[SessionRecord]:
        """Validates a session token, returning the record if valid and unexpired."""
        record = self._sessions_by_token.get(token)
        if not record:
            return None
        if record.is_expired:
            self.close_session(record.session_id)
            return None
        record.last_activity = time.time()
        return record

    def activate_session(self, token: str) -> Optional[SessionRecord]:
        """Marks a session as actively streaming over WebSocket."""
        record = self.validate_token(token)
        if record:
            record.is_active = True
            log_event(logger, 20, "session_activated", "WebSocket stream active", session_id=record.session_id)
        return record

    def close_session(self, session_id_or_token: str) -> None:
        """Closes and removes an active or expired session."""
        token = self._tokens_by_session_id.get(session_id_or_token)
        if token:
            record = self._sessions_by_token.pop(token, None)
            self._tokens_by_session_id.pop(session_id_or_token, None)
        else:
            record = self._sessions_by_token.pop(session_id_or_token, None)
            if record:
                self._tokens_by_session_id.pop(record.session_id, None)

        if record:
            log_event(
                logger,
                20,
                "session_closed",
                "Streaming session terminated",
                session_id=record.session_id,
                chunks_processed=record.chunks_processed,
            )

    def cleanup_expired(self) -> int:
        """Removes all expired sessions from memory, returning count removed."""
        now = time.time()
        expired_tokens = [tok for tok, rec in self._sessions_by_token.items() if rec.expires_at < now]
        for tok in expired_tokens:
            rec = self._sessions_by_token.pop(tok, None)
            if rec:
                self._tokens_by_session_id.pop(rec.session_id, None)
        return len(expired_tokens)


# --- FastAPI Route Definitions ---

if _HAS_FASTAPI:
    class SessionRequest(BaseModel):
        device_role: str = Field(default="guardian", description="Role of caller: guardian or member")
        lang: str = Field(default="auto", description="Preferred audio language code (en, hi, auto)")
        client_version: Optional[str] = Field(default=None, description="Client software version")

    class SessionResponse(BaseModel):
        session_id: str
        token: str
        expires_at: float
        sample_rate: int
        channels: int
        chunk_duration_sec: float
        websocket_url: str

    router = APIRouter(prefix="/v1", tags=["Session"])

    @router.post("/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
    async def create_session_endpoint(req: SessionRequest, request: Request) -> Dict[str, Any]:
        """Issues an ephemeral streaming token for audio ingest."""
        session_mgr: SessionManager = request.app.state.session_manager
        cfg = request.app.state.config

        try:
            record = session_mgr.create_session(
                device_role=req.device_role,
                lang=req.lang,
                ttl_sec=cfg.session_ttl_sec,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

        return {
            "session_id": record.session_id,
            "token": record.token,
            "expires_at": record.expires_at,
            "sample_rate": cfg.sample_rate,
            "channels": cfg.channels,
            "chunk_duration_sec": cfg.chunk_duration_sec,
            "websocket_url": f"/v1/stream?token={record.token}",
        }
else:
    router = None
