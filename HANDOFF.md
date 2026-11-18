# HANDOFF (updated: 2026-11-18, Phase 9 DONE, Phase 10 TODO)

## What this project is (3 lines)
Family Voice Shield is an anti-voice-clone scam protection system for families.
It proves caller identity using an offline, zero-knowledge rotating family code (60-second synchronized 6-digit TOTP) with directional keys and lockout protection.
An accompanying AI warning layer (scam language + synthetic speech detection) automatically triggers the challenge prompt when risk is detected.

## Current state
- Phase status: 0 DONE, 1 DONE, 2 DONE, 3 DONE, 4 DONE, 5 DONE, 6 DONE, 7 DONE, 8 DONE, 9 DONE, 10 TODO
- Built in Phases 0 through 9:
  - Repository monorepo layout (`core/`, `mobile/`, `server/`, `ml/`, `demo/`, `infra/`, `tests/`, `docs/`)
  - Complete documentation system (`docs/00` through `docs/09`)
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
  - Telephony channel and degradation codec simulator (`ml/telephony_codec.py`) supporting ITU-T G.711 $\mu$-law/A-law, 300-3400 Hz voice bandpass filter, 8 kHz decimation/resampling, and packet jitter simulation
  - Acoustic anti-spoofing engine (`ml/antispoof_engine.py`) measuring ZCR variance, pitch stability, and crest factor, with carrier telephony compensation and ONNX runtime support
  - Calibrated multimodal logistic fusion engine (`ml/fusion.py`) combining acoustic, semantic, and context signals with fail-safe overrides
  - Alert tier state machine (`core/alert_tiers.py`) with asymmetric hysteresis debouncing (fast escalation, damped de-escalation) and HMAC-SHA256 emergency broadcast signing
  - Interactive dual-device web simulator (`demo/web_simulator.py`) featuring real-time AI Threat Simulator presets, animated alert banners, and bilingual audio TTS guidance
  - Scripted evaluation scenario catalog (`demo/scenarios.py`) with 5 realistic Indian fraud tactics and edge cases (S1: Fake Accident, S2: Digital Arrest, S3: Benign Family, S4: Relay Attack Defense, S5: Covert Duress Call)
  - Standalone telephony streaming replay test harness (`demo/telephony_replay.py`) simulating degraded G.711 carrier audio through `StreamScorer` with real-time SLA verification ($\le 8\text{s}$) and p50/p95 latency profiling
  - Web simulator walkthrough enhancements (`demo/web_simulator.py`) adding interactive scenario selector bar, full scenario runner, step-by-step playback, and real-time event log
  - Adversarial red-team test suite (`tests/test_redteam.py`) covering semantic evasion, deepfake telephony degradation, fusion overrides, and cryptographic attacks
  - Automated privacy and security audit test suite (`tests/test_privacy_security_audit.py`) validating Rule 7 zero-disk persistence, memory buffer purge, and logger scrubbing
  - Hardening and recovery test suite (`tests/test_hardening_recovery.py`) validating concurrency limits, backpressure memory caps, and disconnect teardown
  - Automated empirical benchmark runner (`demo/evaluate_system.py`) deriving precision (100%), recall (94.7%), specificity (100%), F1-score (0.973), and latencies
  - Formal evaluation report (`docs/09_EVALUATION_REPORT.md`)
  - Docker containerization (`infra/Dockerfile` and `infra/docker-compose.yml`)
  - Audio replay client (`server/client_replay.py`) and Flutter/Dart streaming client (`mobile/audio_stream_client.dart`)
  - Comprehensive unit and integration test suite (135 total tests across 15 test suites in `tests/`, 100% passing).
- Not built / left off:
  - Phase 10: Pitch & Release (slide deck, demo video script, final README polish)
- Known bugs and traps:
  - Call audio is not directly accessible by 3rd-party apps on standard iOS/Android; MVP uses speakerphone mic or Twilio stream.
  - Zero disk audio persistence must be strictly maintained (Rule 7).
  - Directional keys are critical to prevent relay (A->B must differ from B->A).
  - 60-second time window is configured per ADR-006 for senior accessibility.

## How to run and test (exact commands)
- Run unit test suite:
  `python -m unittest discover tests`
- Run empirical benchmark evaluation runner:
  `python -m demo.evaluate_system`
- Run red-team adversarial tests:
  `python -m unittest tests/test_redteam.py`
- Run zero-disk privacy and security audit:
  `python -m unittest tests/test_privacy_security_audit.py`
- Run failure recovery and hardening tests:
  `python -m unittest tests/test_hardening_recovery.py`
- Run telephony replay harness across all scenarios:
  `python -m demo.telephony_replay --all`
- Run FastAPI streaming server:
  `uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload`
- Run interactive dual-device web simulator with walkthrough:
  `python demo/web_simulator.py 8080` (open http://localhost:8080 in browser)
- Run via Docker:
  `docker compose -f infra/docker-compose.yml up --build`

## Key decisions
- ADR-001: Monorepo layout with pure-function crypto core in Python & Dart.
- ADR-002: Identity layer as primary protection; AI as closed-loop trigger.
- ADR-003: Platform call audio fallback strategy (speakerphone mic + Twilio stream).
- ADR-004: Code format: 6 digits and 2-word phonetic lexicon (superseded by ADR-006).
- ADR-005: Directional key derivation with HKDF-SHA256 (`FVS1|A->B` vs `FVS1|B->A`).
- ADR-006: Pure 6-digit TOTP, 60s rotation, contact-based pairing with feature phone fallback.

## Next step
Phase 9 is DONE. Awaiting user instruction before pushing to GitHub or proceeding to Phase 10: Pitch & Release (`phase/10-release`).
