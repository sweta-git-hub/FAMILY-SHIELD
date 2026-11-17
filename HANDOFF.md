# HANDOFF (updated: 2026-11-17, Phase 2 DONE, Phase 3 TODO)

## What this project is (3 lines)
Family Voice Shield is an anti-voice-clone scam protection system for families.
It proves caller identity using an offline, zero-knowledge rotating family code (60-second synchronized 6-digit TOTP) with directional keys and lockout protection.
An accompanying AI warning layer (scam language + synthetic speech detection) automatically triggers the challenge prompt when risk is detected.

## Current state
- Phase status: 0 DONE, 1 DONE, 2 DONE, 3 TODO, 4 TODO, 5 TODO, 6 TODO, 7 TODO, 8 TODO, 9 TODO, 10 TODO
- Built in Phases 0, 1 & 2:
  - Repository monorepo layout (`core/`, `mobile/`, `server/`, `ml/`, `demo/`, `infra/`, `tests/`, `docs/`)
  - Complete documentation system (`docs/00` through `docs/08`)
  - `RULE.md` agent operating rules and permission gates
  - `README.md` and `HANDOFF.md`
  - `.gitignore`, `.env.example`, `pyproject.toml`
  - Core cryptographic engine in Python (`core/crypto.py`) and Dart (`core/crypto.dart`)
  - E.164 phone number utility & contact normalization (`core/phone_util.py`)
  - Zero-knowledge contact pairing protocol & directional keys (`core/pairing.py`)
  - Tamper-evident PBKDF2/HMAC encrypted vault (`core/storage.py`)
  - Live side-by-side dual-phone web simulator with 60s countdown ticker (`demo/web_simulator.py`)
  - Automated test suite (`tests/test_crypto.py`, `tests/test_pairing.py`, `tests/test_storage.py`) passing 100% of 24 unit and parity tests.
- Not built / left off:
  - Phase 3: Verify-Caller UI & elderly UX (Hindi/English TTS prompts, high-contrast big buttons)
  - Phase 4-7: Backend streaming & AI engines (Whisper STT, anti-spoofing ONNX, fusion alerts)
- Known bugs and traps:
  - Call audio is not directly accessible by 3rd-party apps on standard iOS/Android; MVP uses speakerphone mic or Twilio stream.
  - Directional keys are critical to prevent relay (A->B must differ from B->A).
  - 60-second time window is configured per ADR-006 for senior accessibility.

## How to run and test (exact commands)
- Run unit tests:
  `python -m unittest discover tests`
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
Awaiting developer permission (Gate G1) to start Phase 3: Verify-Caller UI & elderly accessibility UX.
