# 02 Phase Plan & Status Board

## Status Board

| Phase | Name | Branch | Goal | Status | Built | Left off | Decisions |
|---|---|---|---|---|---|---|---|
| 0 | Bootstrap & Docs | `phase/00-bootstrap` | Monorepo scaffold, docs skeleton, lint setup | DONE | Repo layout, docs/00-08, RULE.md, HANDOFF.md, README.md, pyproject.toml | CI lint hooks | ADR-001, ADR-002, ADR-003, ADR-004, ADR-005 |
| 1 | Crypto Core | `phase/01-crypto-core` | TOTP, HKDF, words, lockout, duress in Python & Dart | TODO | - | Awaiting G1 permission | ADR-004, ADR-005 |
| 2 | Pairing & Storage | `phase/02-pairing` | QR pairing, Keystore/Keychain, offline sync | TODO | - | - | - |
| 3 | Verify-Caller UX | `phase/03-verify-flow` | Big buttons, Hindi/English TTS, practice call | TODO | - | - | - |
| 4 | Backend Stream | `phase/04-backend-stream` | FastAPI, WebSocket audio stream, chunker | TODO | - | - | - |
| 5 | Scam Engine | `phase/05-scam-engine` | STT wrapper, lexicon, noisy-OR classifier | TODO | - | - | - |
| 6 | Anti-Spoof | `phase/06-antispoof` | Telephony simulator, ONNX model inference | TODO | - | - | - |
| 7 | Fusion & Alerts | `phase/07-fusion-alerts` | Logistic fusion, alert tiers, client triggers | TODO | - | - | - |
| 8 | Realistic Demo | `phase/08-demo-path` | Telephony/replay demo path, scripted cases | TODO | - | - | - |
| 9 | Eval & Hardening | `phase/09-eval-hardening` | Red-team tests, privacy audit, metrics report | TODO | - | - | - |
| 10 | Pitch & Release | `phase/10-release` | Slide deck, fallback video, README runbook | TODO | - | - | - |

---

## Phase Details

### Phase 0: Bootstrap and Documentation Scaffold
- **Branch**: `phase/00-bootstrap`
- **Time-box**: 1.5 h
- **In scope**: Repository layout, docs/00 to docs/08, RULE.md, HANDOFF.md, ADR-001/002/003.
- **Out of scope**: Application code, models, audio capture.
- **Acceptance criteria**:
  - Fresh workspace tells a new agent what to do in under 10 minutes via `HANDOFF.md`.
  - docs/00 to docs/08 exist with real technical specifications.

### Phase 1: Crypto Core (TOTP, HKDF, Words, Lockout, Duress)
- **Branch**: `phase/01-crypto-core`
- **Time-box**: 2.0 h
- **In scope**:
  - Pure HOTP (RFC 4226) and TOTP (RFC 6238) implementations.
  - HKDF-SHA256 directional key derivation (`FVS1|A->B` vs `FVS1|B->A`).
  - 6-digit numeric and 2-word phonetic representations (2,048-word BIP-39 lexicon).
  - Verification window (-1, 0, +1 time steps) to handle clock skew.
  - Fail-closed lockout state machine (3 failed attempts -> lockout).
  - Duress code derivation and detection.
  - Shared JSON test vector file (`tests/fixtures/crypto_test_vectors.json`).
  - Python implementation (`core/crypto.py`) + Dart implementation (`core/crypto.dart`).
  - 100% test coverage with automated unit tests.
- **Out of scope**: UI, persistent secure storage, network transport.
- **Acceptance criteria**:
  - 100% of RFC 4226 and RFC 6238 vectors pass.
  - Parity test produces identical codes across test vectors.
  - Lockout fails closed.
