"""WebSocket streaming endpoint for Family Voice Shield audio ingestion.

Handles bidirectional communication: receives raw 16-bit PCM frames from client,
buffers via AudioChunker, and returns real-time risk scores from MockScorer.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict

try:
    from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status  # type: ignore
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False

from server.chunker import AudioChunker
from server.logger import get_logger, log_event
from server.scorer import StreamScorer
from server.session import SessionManager

logger = get_logger("stream")

if _HAS_FASTAPI:
    router = APIRouter(prefix="/v1", tags=["Stream"])

    @router.websocket("/stream")
    async def websocket_stream_endpoint(
        websocket: WebSocket,
        token: str = Query(..., description="Ephemeral session token issued by POST /v1/session")
    ) -> None:
        """Bidirectional WebSocket endpoint for PCM audio streaming and risk feedback."""
        session_mgr: SessionManager = websocket.app.state.session_manager
        cfg = websocket.app.state.config

        # 1. Authenticate token
        record = session_mgr.activate_session(token)
        if not record:
            log_event(logger, 30, "ws_unauthorized", "WebSocket connection rejected: invalid or expired token")
            await websocket.close(code=4001, reason="Unauthorized: invalid or expired token")
            return

        await websocket.accept()
        session_id = record.session_id
        start_time = time.time()

        log_event(logger, 20, "ws_connected", "Client connected to audio stream", session_id=session_id)

        # 2. Per-connection chunker and scorer instances
        chunker = AudioChunker(
            sample_rate=cfg.sample_rate,
            channels=cfg.channels,
            sample_width=cfg.sample_width,
            chunk_duration_sec=cfg.chunk_duration_sec,
            chunk_stride_sec=cfg.chunk_stride_sec,
        )
        scorer = StreamScorer()
        call_context: Dict[str, Any] = {}

        try:
            while True:
                message = await websocket.receive()

                # Handle binary PCM audio data
                if "bytes" in message and message["bytes"]:
                    pcm_data = message["bytes"]
                    chunks = chunker.push_pcm(pcm_data)

                    for chunk in chunks:
                        record.chunks_processed += 1
                        score = scorer.score_chunk(chunk, call_context)

                        # Deliver JSON score frame back to client
                        await websocket.send_text(json.dumps(score.to_dict()))

                        log_event(
                            logger,
                            20,
                            "chunk_scored",
                            "Chunk processed and scored",
                            session_id=session_id,
                            chunk_index=chunk.chunk_index,
                            t=score.t,
                            risk=score.risk,
                            tier=score.tier,
                            has_speech=chunk.has_speech,
                        )

                # Handle JSON control frames (start, context, end)
                elif "text" in message and message["text"]:
                    try:
                        data = json.loads(message["text"])
                    except json.JSONDecodeError:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "code": "invalid_json",
                            "message": "Malformed JSON payload"
                        }))
                        continue

                    msg_type = data.get("type")

                    if msg_type == "start":
                        sample_rate = data.get("sr", cfg.sample_rate)
                        channels = data.get("channels", cfg.channels)
                        log_event(
                            logger,
                            20,
                            "stream_start_handshake",
                            "Stream start handshake acknowledged",
                            session_id=session_id,
                            sr=sample_rate,
                            channels=channels,
                        )
                        await websocket.send_text(json.dumps({
                            "type": "ready",
                            "session": session_id,
                            "sr": cfg.sample_rate,
                            "chunk_duration_sec": cfg.chunk_duration_sec,
                        }))

                    elif msg_type == "context":
                        call_context.update({
                            k: v for k, v in data.items() if k != "type"
                        })
                        log_event(
                            logger,
                            20,
                            "context_updated",
                            "Call context received",
                            session_id=session_id,
                            context_keys=list(call_context.keys()),
                        )

                    elif msg_type == "broadcast":
                        # Dispatches signed emergency family notification (Phase 7)
                        phone = data.get("phone", "+919876543210")
                        last_risk = 0.85 if scorer.alert_state_machine.current_tier.value == "RED" else 0.50
                        notif = scorer.alert_state_machine.generate_emergency_notification(
                            target_phone=phone,
                            fused_risk=last_risk,
                            dominant_modality="multimodal_alert",
                            reasons=["user_emergency_broadcast"],
                        )
                        await websocket.send_text(json.dumps({
                            "type": "broadcast_ack",
                            "notification": notif.to_dict(),
                        }))
                        log_event(
                            logger,
                            20,
                            "ws_emergency_broadcast",
                            "Emergency family notification dispatched",
                            session_id=session_id,
                            notification_id=notif.notification_id,
                        )

                    elif msg_type == "end":
                        log_event(logger, 20, "stream_end_requested", "Client requested stream teardown", session_id=session_id)
                        await websocket.close(code=1000, reason="Normal stream end")
                        break

        except WebSocketDisconnect:
            log_event(logger, 20, "ws_disconnect", "WebSocket disconnected by client", session_id=session_id)
        except Exception as exc:
            log_event(logger, 40, "ws_error", f"WebSocket exception: {str(exc)}", session_id=session_id)
            try:
                await websocket.close(code=1011, reason="Internal server error")
            except Exception:
                pass
        finally:
            duration = round(time.time() - start_time, 2)
            log_event(
                logger,
                20,
                "stream_session_summary",
                "Stream session ended",
                session_id=session_id,
                duration_sec=duration,
                chunks_emitted=chunker.chunks_emitted,
                bytes_received=chunker.total_bytes_received,
            )
            chunker.reset()
            session_mgr.close_session(session_id)
else:
    router = None
