# 07 API Contracts (Draft / Reference)

## WebSocket Stream: `/v1/stream?token=<session_token>`

### Client -> Server
1. Handshake config:
```json
{"type": "start", "session": "uuid", "lang": "auto", "sr": 16000, "channels": 1}
```
2. Raw 16-bit PCM binary frames (100 ms chunks).
3. Call context:
```json
{"type": "context", "unknown_number": true, "claims_relative": true, "hour": 14}
```
4. Teardown:
```json
{"type": "end"}
```

### Server -> Client
```json
{
  "type": "score",
  "t": 12.0,
  "s_a": 0.71,
  "s_t": 0.64,
  "s_c": 0.50,
  "risk": 0.69,
  "tier": "AMBER",
  "reasons": ["urgency", "secrecy", "new_number"],
  "prompt": "ask_for_code"
}
```

## REST Endpoints
- `POST /v1/session`: Request transient streaming session token.
- `GET /v1/health`: Server health check.
- `POST /v1/notify`: Push metadata notification to paired family devices via FCM.
