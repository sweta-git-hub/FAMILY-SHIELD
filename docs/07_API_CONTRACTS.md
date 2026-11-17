# 07 API Contracts

## 1. REST Endpoints

### 1.1 Health Check: `GET /v1/health`
Confirms streaming service operational status.

**Response** (`200 OK`):
```json
{
  "status": "ok",
  "service": "family-voice-shield",
  "version": "0.4.0",
  "sample_rate": 16000,
  "channels": 1,
  "chunk_duration_sec": 3.0,
  "active_sessions": 0
}
```

### 1.2 Ephemeral Session Token: `POST /v1/session`
Requests a short-lived bearer token required to connect to the WebSocket audio stream. Tokens are stored purely in-memory and automatically expire after `session_ttl_sec` (default 3600s).

**Request Body** (`application/json`):
```json
{
  "device_role": "guardian",
  "lang": "hi",
  "client_version": "0.4.0"
}
```

**Response** (`201 Created`):
```json
{
  "session_id": "7f8b9a1c-3d2e-4f5a-8b9c-0d1e2f3a4b5c",
  "token": "dGhpcy1pcy1hLXNlY3VyZS11cmxzYWZlLXRva2Vu...",
  "expires_at": 1700003600.0,
  "sample_rate": 16000,
  "channels": 1,
  "chunk_duration_sec": 3.0,
  "websocket_url": "/v1/stream?token=dGhpcy1pcy1hLXNlY3VyZS11cmxzYWZlLXRva2Vu..."
}
```

**Error Responses**:
- `503 Service Unavailable`: Server has reached `max_active_sessions` concurrent limit.

---

## 2. WebSocket Audio Stream: `/v1/stream?token=<session_token>`

All real-time audio analysis occurs over this bidirectional WebSocket connection.

### Authentication & Handshake
Clients must provide a valid `token` query parameter. If the token is invalid or expired, the server terminates the connection with WebSocket close code `4001` (`Unauthorized: invalid or expired token`).

### 2.1 Client -> Server Messages

#### A. Handshake Frame (Text / JSON)
Immediately sent by client upon opening socket:
```json
{
  "type": "start",
  "session": "7f8b9a1c-3d2e-4f5a-8b9c-0d1e2f3a4b5c",
  "lang": "hi",
  "sr": 16000,
  "channels": 1
}
```

#### B. Audio Frames (Binary)
Continuous raw 16-bit linear PCM audio (16 kHz, mono, little-endian signed 16-bit integers).
- Frame size: Paced 100 ms packets ($1600 \text{ samples} \times 2 \text{ bytes} = 3,200 \text{ bytes}$).
- Transmitted directly as binary WebSocket frames.

#### C. Call Context Frame (Text / JSON, Optional)
Metadata provided by dialer or incoming call detector:
```json
{
  "type": "context",
  "unknown_number": true,
  "claims_relative": true,
  "hour": 14
}
```

#### D. Teardown Frame (Text / JSON)
Gracefully terminates the streaming session:
```json
{
  "type": "end"
}
```

---

### 2.2 Server -> Client Messages

#### A. Ready Acknowledgment (Text / JSON)
Sent in response to `"start"` handshake:
```json
{
  "type": "ready",
  "session": "7f8b9a1c-3d2e-4f5a-8b9c-0d1e2f3a4b5c",
  "sr": 16000,
  "chunk_duration_sec": 3.0
}
```

#### B. Risk Score Feedback Frame (Text / JSON)
Emitted every 1.0 second as each 3.0-second chunk completes:
```json
{
  "type": "score",
  "t": 3.0,
  "s_a": 0.15,
  "s_t": 0.10,
  "s_c": 0.20,
  "risk": 0.16,
  "tier": "GREEN",
  "reasons": [],
  "prompt": "normal",
  "mock": true
}
```

**Score Field Definitions**:
- `t`: Elapsed call time in seconds.
- `s_a`: Acoustic synthetic speech probability $[0.0 - 1.0]$ (AASIST model in Phase 6).
- `s_t`: Semantic scam language probability $[0.0 - 1.0]$ (Whisper + Classifier in Phase 5).
- `s_c`: Call context risk score $[0.0 - 1.0]$.
- `risk`: Fused composite scam risk probability $[0.0 - 1.0]$.
- `tier`: Classification tier:
  - `GREEN` ($\text{risk} < 0.40$): Low risk, standard display.
  - `AMBER` ($0.40 \le \text{risk} < 0.70$): Suspicious call; displays warning prompt.
  - `RED` ($\text{risk} \ge 0.70$): Critical scam detected; prompts guardian to demand family rotating code.
- `reasons`: Machine-readable triggers (e.g. `["urgency", "secrecy", "new_number"]`).
- `prompt`: Recommended UX action (`"normal"` or `"ask_for_code"`).
- `mock`: Boolean indicating mock scoring (`true` until Phase 5/6 real models are wired).

#### C. Error Frame (Text / JSON)
```json
{
  "type": "error",
  "code": "invalid_json",
  "message": "Malformed JSON payload"
}
```

---

## 3. WebSocket Close Codes
- `1000`: Normal closure upon `"end"` frame.
- `4001`: Unauthorized / missing or expired session token.
- `1011`: Internal server exception.
