# 06 Runbook

## Environment Requirements
- Python 3.10+
- (Later phases) Flutter 3.x / Dart 3.x
- Docker 24+ & Docker Compose (optional for containerized runs)

---

## 1. Automated Unit & Integration Tests

Run the complete test suite (crypto, pairing, storage, UX, chunker, session, scorer, and streaming endpoints):
```bash
python -m unittest discover tests
```

Expected output:
```
Ran 135 tests in ~6.5s
OK
```

### Test Suite Inventory:
1. `tests/test_crypto.py` (9 tests): RFC 4226 HOTP, RFC 6238 TOTP, HKDF directional keys, duress derivation, BIP-39 phonetic codec, skew window, 3-strike lockout, 1000 parity vectors.
2. `tests/test_pairing.py` (6 tests): E.164 phone normalization, zero-knowledge invite handshake, peer mismatch rejection, 60s TOTP synchronization, directional isolation ($A \to B \neq B \to A$), and lockout integration.
3. `tests/test_storage.py` (9 tests): `SecureVault` operations, peer phone lookup, revocation, PBKDF2/HMAC export/import, tamper detection fail-closed.
4. `tests/test_elderly_ux.py` (7 tests): Bilingual prompt catalog (EN/HI), language toggle, accessibility contrast, emergency callback URI, family SOS broadcast, isolated practice mode.
5. `tests/test_session.py` (6 tests): Ephemeral session creation, token validation, activation, TTL expiration, closure, and capacity throttling.
6. `tests/test_chunker.py` (9 tests): 16 kHz 16-bit PCM chunk sizing (3.0s = 96,000 bytes), sliding stride (1.0s = 32,000 bytes), 100ms packet feeding, SimpleEnergyVAD silence vs speech classification, ring buffer overflow eviction, and buffer reset.
7. `tests/test_scorer.py` (3 tests): `MockScorer` contract compliance, silence GREEN tier classification, call context risk elevation (`unknown_number` + `claims_relative`).
8. `tests/test_backend_stream.py` (6 tests): `GET /v1/health`, `POST /v1/session`, WebSocket unauthorized rejection (close code 4001), WebSocket handshake (`start` $\to$ `ready`), live PCM streaming, score pushes, clean teardown (`end`), client reconnect, and replay statistics.
9. `tests/test_scam_engine.py` (13 tests): Multilingual scam lexicon extraction, Devanagari/Hinglish patterns, Bayesian Noisy-OR mathematical monotonicity, and in-memory STT engine.
10. `tests/test_antispoof.py` (12 tests): G.711 $\mu$-law/A-law codec fidelity, 8 kHz decimation, bandpass filtering, packet jitter, and acoustic artifact scoring ($s_a$).
11. `tests/test_fusion_alerts.py` (8 tests): Calibrated multimodal logistic fusion, fail-safe critical threat overrides ($\ge 0.70$), alert tier state machine with hysteresis debouncing, and HMAC-signed emergency broadcast alerts.
12. `tests/test_demo_scenarios.py` (20 tests): 5 structured evaluation scenarios (S1-S5), telephony replay harness, web simulator stepping, and benchmark metrics verification.
13. `tests/test_redteam.py` (15 tests): Adversarial scam lexicon evasion, polite phrasing, dilution attacks, deepfake detection under carrier telephony degradation, and cryptographic replay/directional key defenses.
14. `tests/test_privacy_security_audit.py` (4 tests): Zero-disk persistence audit across high-volume streams (Rule 7), in-memory buffer purge, sensitive log sanitization, and vault tamper fail-closed defense.
15. `tests/test_hardening_recovery.py` (5 tests): Concurrency capacity caps, odd-byte PCM handling, extreme signal clipping/DC offset safety, 12s buffer capacity eviction, and abrupt WebSocket disconnect cleanup.

---

## 2. Running the Audio Streaming Server (Phase 4)

### 2.1 Local Python Process
Install dependencies:
```bash
pip install -r server/requirements.txt
```

Launch the FastAPI streaming server:
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify health check:
```bash
curl http://localhost:8000/v1/health
```

Expected JSON response:
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

### 2.2 Docker Container
Build and start the streaming server container:
```bash
docker compose -f infra/docker-compose.yml up --build -d
```

View container logs:
```bash
docker compose -f infra/docker-compose.yml logs -f
```

Stop container:
```bash
docker compose -f infra/docker-compose.yml down
```

---

## 3. Replay Test Client (Simulated Microphone Audio)

Stream synthetic or real audio into the running server to measure round-trip score latency:
```bash
python server/client_replay.py --host localhost --port 8000 --duration 10.0
```

Or stream a custom 16 kHz mono WAV file:
```bash
python server/client_replay.py --host localhost --port 8000 --file path/to/sample.wav
```

Expected output:
```
[*] Starting audio streaming client connecting to localhost:8000...
[+] Stream Complete for session: e1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c
    Frames Sent:     100 (320000 bytes)
    Scores Received: 8
    Avg Latency:     14.2 ms
    Min/Max Latency: 8.5 ms / 24.1 ms
    Final Tier:      GREEN (Risk: 0.16)
```

---

## 4. Interactive Dual-Device Web Simulator (Phases 2 & 3 Demo)

Launch the side-by-side interactive simulator in your browser:
```bash
python demo/web_simulator.py 8080
```
Open `http://localhost:8080/` in any browser:
- **Left phone**: Guardian (Mom).
- **Right phone**: Member (Rahul).
- **Language**: Toggle between English and हिंदी to hear and see spoken prompts.
- **Keypad**: Tap digits 0-9 on the large tactile keypad.
- **Emergency Action**: Test "Hang Up & Call Back" to break virtual kidnapping.
- **Practice Mode**: Click "Practice Call Mode" for an isolated training simulation.

---

## 5. Realistic Telephony Replay & Scenario Evaluation (Phase 8)

Family Voice Shield includes a standalone CLI replay runner that simulates G.711 carrier-grade telephony audio streaming through the full detection pipeline:

### 5.1 List All Scenarios
```bash
python -m demo.telephony_replay --list
```

### 5.2 Run All 5 Evaluation Scenarios with SLA Checks
```bash
python -m demo.telephony_replay --all
```
Expected output:
```
================================================================
  Scenario S1: Fake Accident – UPI Demand
================================================================
  Category        : SCAM
  Expected tier   : 🔴 RED
  Actual tier     : 🔴 RED
  All tiers match : ✅ YES
  Time to AMBER   : 4.0s (target ≤ 4.0s)  [✅ SLA MET]
  Time to RED     : 6.0s (target ≤ 6.0s)
  Pipeline Latency : p50=2.8ms  p95=2.9ms  max=2.9ms
  Channel Simulator: G.711 Telephony (8kHz bandpass)

  Chunk Progression:
    [0] 🟢 GREEN    risk=0.001 lat= 2.9ms ✅ "Hello mummy, main aapka beta bol raha hoon, phone su…"
    ...
```

### 5.3 Run a Single Named Scenario with JSON Output
```bash
python -m demo.telephony_replay --scenario S2 --json
```

### 5.4 Live Interactive Walkthrough via Web Simulator
Launch the browser UI:
```bash
python demo/web_simulator.py 8080
```
Open `http://localhost:8080/`:
- **Scenario Selector**: Select any scenario (`S1`–`S5`) from the top evaluation bar.
- **Run Entire Scenario**: Replays the full multi-window call with real-time SLA badge verification.
- **Step Next Chunk**: Advances window-by-window for interactive presentations.
- **Live Event Log**: Inspects real-time risk scores, latencies, and audible bilingual TTS guidance.

---

## 6. Resetting State
- **Server sessions**: Automatically expire in memory after TTL; restart server or send `{"type": "end"}` to terminate immediately.
- **Client Vault**: Vault records and strike counters can be reset via the simulator UI ("Reset Strikes") or by re-instantiating fresh in-memory `SecureVault` instances.

---

## 7. Running System Evaluation & Empirical Benchmarks (Phase 9)

Run the automated 30-case empirical evaluation harness to measure precision, recall, F1, false positive rate, and processing latency:
```bash
python -m demo.evaluate_system
```

Or export machine-readable JSON metrics for automated evaluation reporting:
```bash
python -m demo.evaluate_system --json
```

---

## 8. Running Red-Team & Privacy Audit Suites (Phase 9)

Execute the targeted adversarial red-team penetration tests:
```bash
python -m unittest tests/test_redteam.py
```

Execute the automated zero-disk privacy and logger sanitization audit:
```bash
python -m unittest tests/test_privacy_security_audit.py
```

Execute the concurrency, packet corruption, and failure recovery tests:
```bash
python -m unittest tests/test_hardening_recovery.py
```
