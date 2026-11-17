# HANDOFF (updated: 2026-11-18, Phase 5 DONE, Phase 6 TODO)

## What this project is (3 lines)
Family Voice Shield is an anti-voice-clone scam protection system for families.
It proves caller identity using an offline, zero-knowledge rotating family code (60-second synchronized 6-digit TOTP) with directional keys and lockout protection.
An accompanying AI warning layer (scam language + synthetic speech detection) automatically triggers the challenge prompt when risk is detected.

## Current state
- Phase status: 0 DONE, 1 DONE, 2 DONE, 3 DONE, 4 DONE, 5 DONE, 6 TODO, 7 TODO, 8 TODO, 9 TODO, 10 TODO
- Built in Phases 0, 1, 2, 3, 4 & 5:
  - Repository monorepo layout (`core/`, `mobile/`, `server/`, `ml/`, `demo/`, `infra/`, `tests/`, `docs/`)
  - Complete documentation system (`docs/00` through `docs/08`)
  - `RULE.md` agent operating rules and permission gates
  - `README.md` and `HANDOFF.md`
  - `.gitignore`, `.env.example`, `pyproject.toml`
  - Core cryptographic engine in Python (`core/crypto.py`) and Dart (`core/crypto.dart`)
  - E.164 phone number utility & contact normalization (`core/phone_util.py`)
  - Zero-knowledge contact pairing protocol & directional keys (`core/pairing.py`)
  - Tamper-evident PBKDF2/HMAC encrypted vault (`core/storage.py`)
  - Elderly accessibility engine, bilingual speech prompts, and practice call session (`core/elderly_ux.py`)
  - Live side-by-side dual-phone web simulator with tactile keypad, speech synthesis, high contrast, and emergency safe actions (`demo/web_simulator.py`)
  - FastAPI streaming server (`server/main.py`, `server/config.py`, `server/logger.py`) with `GET /v1/health`
  - Ephemeral session manager (`server/session.py`) issuing transient tokens via `POST /v1/session`
  - In-memory circular PCM audio chunker with VAD hook (`server/chunker.py`) with zero disk persistence
  - WebSocket streaming endpoint (`server/stream.py`) with real-time `StreamScorer` (`server/scorer.py`)
  - Multilingual scam lexicon and taxonomy (`ml/scam_lexicon.py`) covering 6 categories across Hindi, English, and Hinglish
  - Probabilistic Noisy-OR Bayesian scam intent classifier (`ml/scam_classifier.py`)
  - Privacy-preserving in-memory STT engine wrapper (`ml/stt_engine.py`) supporting Faster-Whisper and mock testing
  - Docker containerization (`infra/Dockerfile` and `infra/docker-compose.yml`)
  - Audio replay client (`server/client_replay.py`) and Flutter/Dart streaming client (`mobile/audio_stream_client.dart`)
  - Comprehensive unit and integration test suite (68 total tests across 9 test suites in `tests/`).
- Not built / left off:
  - Phase 6: Acoustic Anti-Spoofing (telephony codec simulation, AASIST/ONNX inference)
  - Phase 7: Multimodal Fusion & Client Alerts
- Known bugs and traps:
  - Call audio is not directly accessible by 3rd-party apps on standard iOS/Android; MVP uses speakerphone mic or Twilio stream.
  - Zero disk audio persistence must be strictly maintained (Rule 7).
  - Directional keys are critical to prevent relay (A->B must differ from B->A).
  - 60-second time window is configured per ADR-006 for senior accessibility.

## How to run and test (exact commands)
- Run unit test suite:
  `python -m unittest discover tests`
- Run FastAPI streaming server:
  `uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload`
- Run replay test client:
  `python server/client_replay.py --host localhost --port 8000 --duration 10.0`
- Run via Docker:
  `docker compose -f infra/docker-compose.yml up --build`
- Run interactive dual-device web simulator:
  `python demo/web_simulator.py 8080` (open http://localhost:8080 in browser)

## Key decisions
- ADR-001: Monorepo layout with pure-function crypto core in Python & Dart.
- ADR-002: Identity layer as primary protection; AI as closed-loop trigger.
- ADR-003: Platform call audio fallback strategy (speakerphone mic + Twilio stream).
- ADR-004: Code format: 6 digits and 2-word phonetic lexicon (superseded by ADR-006).
- ADR-005: Directional key derivation with HKDF-SHA256 (`FVS1|A->B` vs `FVS1|B->A`).
- ADR-006: Pure 6-digit TOTP, 60s rotation, contact-based pairing with feature phone fallback.

## Next step
Phase 5 is DONE. Awaiting user instruction before pushing to GitHub or proceeding to Phase 6: Acoustic Anti-Spoofing (`phase/06-antispoof`).
