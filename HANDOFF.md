# HANDOFF (updated: 2026-11-17, Phase 1 DONE, Phase 2 TODO)

## What this project is (3 lines)
Family Voice Shield is an anti-voice-clone scam protection system for families.
It proves caller identity using an offline, zero-knowledge rotating family code (TOTP/word pairs) with directional keys and lockout protection.
An accompanying AI warning layer (scam language + synthetic speech detection) automatically triggers the challenge prompt when risk is detected.

## Current state
- Phase status: 0 DONE, 1 DONE, 2 TODO, 3 TODO, 4 TODO, 5 TODO, 6 TODO, 7 TODO, 8 TODO, 9 TODO, 10 TODO
- Built in Phase 0 & Phase 1:
  - Repository monorepo layout (`core/`, `mobile/`, `server/`, `ml/`, `demo/`, `infra/`, `tests/`, `docs/`)
  - Complete documentation system (`docs/00` through `docs/08`)
  - `RULE.md` agent operating rules and permission gates
  - `README.md` and `HANDOFF.md`
  - `.gitignore`, `.env.example`, `pyproject.toml`
  - Core cryptographic engine in Python (`core/crypto.py`) and Dart (`core/crypto.dart`)
  - 2,048-word phonetic BIP-39 lexicon (`core/wordlist.py`)
  - Shared test vectors (`tests/fixtures/crypto_test_vectors.json`)
  - Automated test suite (`tests/test_crypto.py`) passing 100% of RFC 4226, RFC 6238, HKDF directional, duress, word encoding, and 1,000 parity vectors.
- Not built / left off:
  - Phase 2: Pairing & secure storage (Flutter shell, QR exchange, Keystore/Keychain)
  - Phase 3: Verify-Caller UI & elderly UX (Hindi/English TTS prompts, practice mode)
  - Phase 4-7: Backend streaming & AI engines
- Known bugs and traps:
  - Call audio is not directly accessible by 3rd-party apps on standard iOS/Android; MVP uses speakerphone mic or Twilio stream.
  - Directional keys are critical to prevent relay (A->B must differ from B->A).
  - Telephony audio is 8 kHz band-limited, which degrades generic anti-spoofing; identity layer is the true security anchor.

## How to run and test (exact commands)
- Run unit tests:
  `python -m unittest discover tests`

## Key decisions
- ADR-001: Monorepo layout with pure-function crypto core in Python & Dart.
- ADR-002: Identity layer as primary protection; AI as closed-loop trigger.
- ADR-003: Platform call audio fallback strategy (speakerphone mic + Twilio stream).
- ADR-004: Code format: 6 digits and 2-word phonetic lexicon.
- ADR-005: Directional key derivation with HKDF-SHA256 (`FVS1|A->B` vs `FVS1|B->A`).

## Next step
Awaiting developer permission (Gate G1) to start Phase 2: Flutter shell, in-person QR pairing, and secure storage on physical/simulated devices.
