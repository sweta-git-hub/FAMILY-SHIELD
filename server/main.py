"""Family Voice Shield - Main FastAPI Application.

Provides REST and WebSocket endpoints for audio streaming and identity verification.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

try:
    from fastapi import FastAPI, Request, status  # type: ignore
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore
    from fastapi.responses import JSONResponse  # type: ignore
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False

from server.config import ServerConfig, load_config
from server.logger import get_logger, log_event, setup_logging
from server.session import SessionManager, router as session_router
from server.stream import router as stream_router

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: Any) -> AsyncGenerator[None, None]:
    """Lifespan context manager for application startup and shutdown."""
    cfg = getattr(app.state, "config", None) or load_config()
    setup_logging(cfg.log_level)
    log_event(logger, logging.INFO, "server_start", "Family Voice Shield server starting", host=cfg.host, port=cfg.port)
    yield
    log_event(logger, logging.INFO, "server_stop", "Family Voice Shield server shutting down")


def create_app(config: ServerConfig | None = None) -> Any:
    """Application factory for FastAPI app."""
    if not _HAS_FASTAPI:
        raise RuntimeError("FastAPI is not installed. Run with installed dependencies.")

    cfg = config or load_config()

    app = FastAPI(
        title="Family Voice Shield Streaming Server",
        description="Zero-knowledge anti-voice-clone streaming gateway",
        version="0.4.0",
        lifespan=lifespan,
    )

    app.state.config = cfg
    app.state.session_manager = SessionManager(
        max_active_sessions=cfg.max_active_sessions,
        default_ttl_sec=cfg.session_ttl_sec
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    if session_router:
        app.include_router(session_router)
    if stream_router:
        app.include_router(stream_router)

    @app.get("/v1/health", status_code=status.HTTP_200_OK)
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint confirming server operational status."""
        session_mgr = getattr(app.state, "session_manager", None)
        active_count = session_mgr.active_count if session_mgr else 0

        return {
            "status": "ok",
            "service": "family-voice-shield",
            "version": "0.4.0",
            "sample_rate": cfg.sample_rate,
            "channels": cfg.channels,
            "chunk_duration_sec": cfg.chunk_duration_sec,
            "active_sessions": active_count,
        }

    return app


# Module-level instance for uvicorn run
if _HAS_FASTAPI:
    app = create_app()
else:
    app = None
