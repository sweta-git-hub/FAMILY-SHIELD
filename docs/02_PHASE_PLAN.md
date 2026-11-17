# 02 Phase Plan & Status Board

## Status Board

| Phase | Name | Branch | Goal | Status | Built | Left off | Decisions |
|---|---|---|---|---|---|---|---|
| 0 | Bootstrap & Docs | `phase/00-bootstrap` | Monorepo scaffold, docs skeleton, lint setup | DONE | Repo layout, docs/00-08, RULE.md, HANDOFF.md, README.md, pyproject.toml | CI lint hooks | ADR-001, ADR-002, ADR-003, ADR-004, ADR-005 |
| 1 | Crypto Core | `phase/01-crypto-core` | TOTP, HKDF, words, lockout, duress in Python & Dart | DONE | core/crypto.py, core/crypto.dart, core/wordlist.py, tests/test_crypto.py | Cross-language runner | ADR-004, ADR-005 |
| 2 | Pairing & Storage | `phase/02-pairing` | Contact/phone pairing, secure vault, live 60s 6-digit sync | DONE | core/phone_util.py, core/pairing.py, core/storage.py, demo/web_simulator.py, tests/test_pairing.py, tests/test_storage.py | Ready for Phase 3 | ADR-006 |
| 3 | Verify-Caller UX | `phase/03-verify-flow` | Big buttons, Hindi/English TTS, practice call | DONE | core/elderly_ux.py, tests/test_elderly_ux.py, demo/web_simulator.py | Ready for Phase 4 | - |
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

### Phase 2: Pairing & Secure Storage (Contact-Based Pairing & 60s 6-Digit Sync)
- **Branch**: `phase/02-pairing`
- **Time-box**: 2.5 h
- **In scope**:
  - Contact-based family member addition: Enter/pick phone number with E.164 normalization (`core/phone_util.py`).
  - Secure Zero-Knowledge Pairing Protocol: Out-of-band / peer token handshake deriving directional HKDF keys without server secret exposure (`core/pairing.py`).
  - Encrypted local secure vault: Multi-member key storage, tamper protection, and revocation (`core/storage.py`).
  - Synchronized 6-digit TOTP generator & remaining-time ticker (RFC 6238, 60s interval per user decision).
  - Dual-device interactive demo interface (web simulator showing Guardian and Member devices side-by-side with real-time 60s countdown and live verification).
  - Comprehensive unit test suite in `tests/test_pairing.py` and `tests/test_storage.py`.
- **Out of scope**:
  - Live acoustic deepfake analysis and Whisper STT (Phases 4-6).
  - Production carrier cellular SMS gateway (mock/local transport for demo).
- **Acceptance criteria**:
  - Entering a phone number successfully creates a verified family pairing.
  - Both paired devices compute identical synchronized 6-digit codes at every 60s step.
  - Directional keys prevent reverse-impersonation ($A \to B \neq B \to A$).
  - Storage vault fails closed on missing/corrupted keys.
  - 100% automated test pass rate.

### Phase 3: Verify-Caller Flow and Elderly Accessibility UX
- **Branch**: `phase/03-verify-flow`
- **Time-box**: 2.5 h
- **In scope**:
  - Elderly-friendly large tactile keypad with oversized 24px+ digit entry and haptic/visual feedback.
  - High-contrast accessibility theme (minimum 7:1 WCAG contrast ratio for low-vision seniors).
  - Bilingual spoken audio prompts in English and Hindi (TTS for prompt, verification, warning, lockout).
  - Safe emergency actions: "Hang Up & Call Back" (`tel:` link to known verified contact) and "Notify Family" emergency broadcast.
  - Practice Call Mode ("अभ्यास कॉल मोड"): zero-risk training simulator allowing seniors to practice without lockout anxiety.
  - Core UX logic module in `core/elderly_ux.py`.
  - Comprehensive unit test suite in `tests/test_elderly_ux.py`.
  - Interactive simulator enhancement in `demo/web_simulator.py`.
- **Out of scope**:
  - Live Whisper STT streaming and ML anti-spoofing (Phases 4-6).
- **Acceptance criteria**:
  - Challenge verification completes in under 15 seconds.
  - Bilingual voice prompts work in both English and Hindi.
  - Practice mode runs isolated from actual live lockout counters.
  - Emergency callback button dials the true saved number.
  - 100% automated test pass rate.


